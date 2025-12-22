from enums import *
import networkx as nx

#==========================================
#   Layer Creation
#==========================================
#All Rooms
#Divide into room types for different layers
#each layer is divided into two sub layers:
    #sl (start_layer) transition > start door
    #el (end_layer) exit door > transition and start door > exit door
    #el also has two copies of each door to make starts and exits distinct nodes
    #connect sl and el through the start door
#this creates a distinct flow through the graph preventing unwanted backtracking

def rooms_to_layers(rooms):
    
    TW, OW = rooms_to_TW_and_OW_layers(rooms)
    BS, BE = rooms_to_branch_layers(rooms)
    J, JB = rooms_to_john_layer(rooms)
    E, EB = rooms_to_entrance_layer(rooms)
    
    layers = [TW, OW, BS, BE, J, JB, E, EB]
    
    return layers
    
    """
    TW_sl, TW_el, OW_sl, OW_el = rooms_to_TW_and_OW_layers(rooms)
    BS_sl, BS_el, BE_sl, BE_el = rooms_to_branch_layers(rooms)
    J_sl, J_el, JB_sl, JB_el = rooms_to_john_layer(rooms)
    E_sl, E_el, EB_sl, EB_el = rooms_to_entrance_layer(rooms)
    
    layers = [TW_sl, TW_el, OW_sl, OW_el, BS_sl, BS_el, BE_sl, BE_el, J_sl, J_el, JB_sl, JB_el, E_sl, E_el, EB_sl, EB_el]
    
    return layers"""

def rooms_to_layer(rooms, layer_id, path_selector = lambda e: True):
    
    print(str(len(rooms)) + " rooms to layer " + str(layer_id))
    
    msg = ""
    
    for room in rooms:
        msg += ", " + str(room.name)
    
    print("rooms: " + msg)
    
    return populate_start_and_exit_layer(rooms, layer_id, path_selector)
    
    """start = nx.DiGraph()
    exit = nx.DiGraph()

    layers = [start, exit]

    def layer_selector(path):
        yield start, exit

    populate_layers(rooms, layers, layer_selector)

    return start, exit"""
    
#TODO: path in exit layer may go both ways for two way paths
#but we want it to be a one way transaction
#start door > exit door > transition
#not
#start door > exit door > start door (or any other possible door) > transition
#so we should make the connecting start door in the exit layer distinct from the "start door" in the exit layer
#so there will be two copies of each door, one used only for exits and one used for only starts
#starts connect to exits only and exits connect to transitions only
#need to modify popualte_layers and add_path_to_layer

LAYER_START_ID = "start"
LAYER_EXIT_ID = "exit"

#start/exit layers are virtual layers within a single greater layer
#each door exits twice in the layer, once in start and once in exit
#providing a way to create distinct directionality as you move through the
#layer and preventing unwanted backtracking
def populate_start_and_exit_layer(rooms, layer_id, path_selector = lambda e: True):
    layer = nx.DiGraph()
    layer_ids = [LAYER_START_ID, LAYER_EXIT_ID]

    for room in rooms:
        room_id = room.name

        layer.add_node(room_id)
        layer.nodes[room_id][LAYER_TYPE] = LAYER_ROOM

       
        for door in room.doors:
            

            #add door and connect room to door
            for layer_type_id in layer_ids:
                
                #Layer name, start/exit, room name, door letter
                door_id = (layer_id, layer_type_id, room.name, door.letter)
                
                layer.add_node(door_id)
                layer.nodes[door_id][LAYER_TYPE] = LAYER_DOOR
                layer.add_edge(room_id, door_id)    

        #add paths between layers
        for path in room.paths:
            if path_selector(path):
                add_start_exit_path_to_layer(room_id, path, layer, layer_id)
    
    return layer

def add_start_exit_path_to_layer(room_id, path, layer, layer_id):
    
    #add start transition node
    #Layer name, start/exit, door type, door direction
    start_transition_id = (layer_id, LAYER_START_ID, path.start_door.door_type, path.start_door.door_dir)
    layer.add_node(start_transition_id)
    
    #marker that this node is a layer node
    layer.nodes[start_transition_id][LAYER_TYPE] = LAYER_TRANSITION
    
    #add exit transition node
    exit_transition_id = (layer_id, LAYER_EXIT_ID, path.exit_door.door_type, path.exit_door.door_dir)
    layer.add_node(exit_transition_id)
    layer.nodes[exit_transition_id][LAYER_TYPE] = LAYER_TRANSITION
    
    #connect start transition type to start door in start layer
    #add path as attribute to this edge
    
    #Layer name, start/exit, room name, door letter
    start_door_id = (layer_id, LAYER_START_ID, room_id, path.start_door.letter)
    layer.add_edge(start_transition_id, start_door_id)
    layer[start_transition_id][start_door_id][LAYER_PATH] = path
    
    #connect exit door to exit transition type to in exit layer
    exit_door_id = (layer_id, LAYER_EXIT_ID, room_id, path.exit_door.letter)
    layer.add_edge(exit_door_id, exit_transition_id)
    
    #connect start door in start layer to exit door in exit layer
    layer.add_edge(start_door_id, exit_door_id)
    
    return

def populate_layers(rooms, layers, layer_selector):
    for room in rooms:
        room_id = room.name

        #add room
        for layer in layers:
            layer.add_node(room_id)
            layer.nodes[room_id][LAYER_TYPE] = LAYER_ROOM

       
        for door in room.doors:
            door_id = (room.name, door.letter)

            #add door and connect room to door
            for layer in layers:
                layer.add_node(door_id)
                layer.nodes[door_id][LAYER_TYPE] = LAYER_DOOR
                layer.add_edge(room_id, door_id)
            
            #connect door to door (virtual, by id)

        #add paths between layers
        #with layers yielded by external selector function
        for path in room.paths:
            for start_layer, exit_layer in layer_selector(path):
                add_path_to_layers(room_id, path, start_layer, exit_layer)

#RoomType.NORMAL
#Four Copies, one with and one without oneway paths
#One layer for starts one layer for exits
def rooms_to_TW_and_OW_layers(all_rooms):
    rooms = filter_rooms(all_rooms, RoomType.NORMAL)

    def valid_path_for_two_way_layer(path):
        return not path.oneway

    TW_layer = rooms_to_layer(rooms, "Two Way", valid_path_for_two_way_layer)
    OW_layer = rooms_to_layer(rooms, "One Way")
    
    TW_layer.graph["name"] = "Two Way"
    OW_layer.graph["name"] = "One Way"
    
    return TW_layer, OW_layer

    """
    TW_start = nx.DiGraph()
    TW_exit = nx.DiGraph()
    OW_start = nx.DiGraph()
    OW_exit = nx.DiGraph()
    
    TW_start.graph["name"] = "TW_start"
    TW_exit.graph["name"] = "TW_exit"
    OW_start.graph["name"] = "OW_start"
    OW_exit.graph["name"] = "OW_exit"

    layers = [TW_start, TW_exit, OW_start, OW_exit]

    def layer_selector(path):
        # OW always
        yield OW_start, OW_exit

        # TW only if not oneway
        if not path.oneway:
            yield TW_start, TW_exit

    populate_layers(rooms, layers, layer_selector)

    return TW_start, TW_exit, OW_start, OW_exit"""

LAYER_PATH = "path"
LAYER_DOOR = "door"
LAYER_ROOM = "room"
LAYER_TRANSITION = "transition"
LAYER_TYPE = "type"

def add_path_to_layers(room_id, path, start_layer, exit_layer):
    
    #add start transition node
    start_transition_id = (path.start_door.door_type, path.start_door.door_dir)
    start_layer.add_node(start_transition_id)
    start_layer.nodes[start_transition_id][LAYER_TYPE] = LAYER_TRANSITION
    
    #add exit transition node
    exit_transition_id = (path.exit_door.door_type, path.exit_door.door_dir)
    exit_layer.add_node(exit_transition_id)
    exit_layer.nodes[exit_transition_id][LAYER_TYPE] = LAYER_TRANSITION
    
    #connect start transition type to start door in start layer
    #add path as attribute to this edge
    start_door_id = (room_id, path.start_door.letter)
    start_layer.add_edge(start_transition_id, start_door_id)
    start_layer[start_transition_id][start_door_id][LAYER_PATH] = path
    
    #connect exit door to exit transition type to in exit layer
    exit_door_id = (room_id, path.exit_door.letter)
    exit_layer.add_edge(exit_door_id, exit_transition_id)
    
    #connect start door in exit layer to exit door in exit layer
    exit_layer.add_edge(start_door_id, exit_door_id)
    
    return

#RoomType.BRANCH
#Four layers
#   BranchType.START or BranchType.ANY  (start and exit)
#   BranchType.END or BranchType.ANY    (start and exit)

def rooms_to_branch_layers(all_rooms):
    
    branch_rooms = filter_rooms(all_rooms, RoomType.BRANCH)
    
    B_any_rooms = filter_rooms_by_branch(branch_rooms, BranchType.ANY)
    B_start_rooms = filter_rooms_by_branch(branch_rooms, BranchType.START)
    B_end_rooms = filter_rooms_by_branch(branch_rooms, BranchType.END)
    
    #TODO: BranchType.MID
    
    B_start_rooms.extend(B_any_rooms)
    B_end_rooms.extend(B_any_rooms)
    
    BS_layer = rooms_to_layer(B_start_rooms, "Branch Start")
    BE_layer = rooms_to_layer(B_end_rooms, "Branch End")
    
    BS_layer.graph["name"] = "Branch Start"
    BE_layer.graph["name"] = "Branch End"
    
    return BS_layer, BE_layer
    
    """
    BS_start_layer, BS_exit_layer = rooms_to_layer(B_start_rooms)
    BE_start_layer, BE_exit_layer = rooms_to_layer(B_end_rooms)
    
    BS_start_layer.graph["name"] = "BS_start_layer"
    BS_exit_layer.graph["name"] = "BS_exit_layer"
    BE_start_layer.graph["name"] = "BE_start_layer"
    BE_exit_layer.graph["name"] = "BE_exit_layer"
    
    return BS_start_layer, BS_exit_layer, BE_start_layer, BE_exit_layer"""

#RoomType.JOHN
def rooms_to_john_layer(all_rooms):
    
    JBE_layer, J_layer = type_and_branch_to_layers(all_rooms, RoomType.JOHN, BranchType.END, "John Branch", "John")
    
    JBE_layer.graph["name"] = "John Branch"
    J_layer.graph["name"] = "John"
    
    return J_layer, JBE_layer 
    
    """
    JBE_start_layer, JBE_exit_layer,  J_start_layer, J_exit_layer = type_and_branch_to_layers(all_rooms, RoomType.JOHN, BranchType.END)
    
    JBE_start_layer.graph["name"] = "JBE_start_layer"
    JBE_exit_layer.graph["name"] = "JBE_exit_layer"
    J_start_layer.graph["name"] = "J_start_layer"
    J_exit_layer.graph["name"] = "J_exit_layer"
    
    return  J_start_layer, J_exit_layer, JBE_start_layer, JBE_exit_layer"""

#RoomType.ENTRANCE
def rooms_to_entrance_layer(all_rooms):
    
    EBS_layer, E_layer = type_and_branch_to_layers(all_rooms, RoomType.ENTRANCE, BranchType.START, "Entrance Branch", "Entrance")
    
    EBS_layer.graph["name"] = "Entrance Branch"
    E_layer.graph["name"] = "Entrance"
    
    return E_layer, EBS_layer
    
    """
    EBS_start_layer, EBS_exit_layer,  E_start_layer, E_exit_layer = type_and_branch_to_layers(all_rooms, RoomType.ENTRANCE, BranchType.START)
    
    EBS_start_layer.graph["name"] = "EBS_start_layer"
    EBS_exit_layer.graph["name"] = "EBS_exit_layer"
    E_start_layer.graph["name"] = "E_start_layer"
    E_exit_layer.graph["name"] = "E_exit_layer"
    
    return E_start_layer, E_exit_layer, EBS_start_layer, EBS_exit_layer """

def type_and_branch_to_layers(all_rooms, room_type, branch_type, branch_layer_id, layer_id):
    
    type_rooms = filter_rooms(all_rooms, room_type)
    type_branch_rooms = filter_rooms_by_branch(type_rooms, branch_type)
    type_rooms = filter_rooms_by_branch(type_rooms, BranchType.NONE)
    
    TBT_layer = rooms_to_layer(type_branch_rooms, branch_layer_id)
    T_layer = rooms_to_layer(type_rooms,layer_id)
    
    return TBT_layer, T_layer
    
    """
    type_rooms = filter_rooms(all_rooms, room_type)
    type_branch_rooms = filter_rooms_by_branch(type_rooms, branch_type)
    type_rooms = filter_rooms_by_branch(type_rooms, BranchType.NONE)
    
    TBT_start_layer, TBT_exit_layer = rooms_to_layer(type_branch_rooms)
    T_start_layer, T_exit_layer = rooms_to_layer(type_rooms)
    
    return T_start_layer, T_exit_layer, TBT_start_layer, TBT_exit_layer"""

def filter_rooms(rooms, room_type):
    return [room for room in rooms if room.room_type == room_type]

def filter_rooms_by_branch(rooms, branch_type):
    return [room for room in rooms if room.branch_type == branch_type]
























