from enums import *
import networkx as nx

#==========================================
#   Layer Creation
#==========================================
#All Rooms
#Divide into room types for different layers
def rooms_to_layers(rooms):
    
    TW_start_layer, TW_exit_layer, OW_start_layer, OW_exit_layer = rooms_to_TW_and_OW_layers(rooms)
    BS_start_layer, BS_exit_layer, BE_start_layer, BE_exit_layer = rooms_to_branch_layers(rooms)
    J_start_layer, J_exit_layer, JB_start_layer, JB_exit_layer = rooms_to_john_layer(rooms)
    E_start_layer, E_exit_layer, EB_start_layer, EB_exit_layer = rooms_to_entrance_layer(rooms)
    
    layers = [TW_start_layer, TW_exit_layer, OW_start_layer, OW_exit_layer, BS_start_layer, BS_exit_layer, BE_start_layer, BE_exit_layer, J_start_layer, J_exit_layer, JB_start_layer, JB_exit_layer, E_start_layer, E_exit_layer, EB_start_layer, EB_exit_layer]
    
    return layers

def rooms_to_layer(rooms):
    start = nx.DiGraph()
    exit = nx.DiGraph()

    layers = [start, exit]

    def layer_selector(path):
        yield start, exit

    populate_layers(rooms, layers, layer_selector)

    return start, exit
    
#TODO: path in exit layer may go both ways for two way paths
#but we want it to be a one way transaction
#start door > exit door > transition
#not
#start door > exit door > start door (or any other possible door) > transition
#so we should make the connecting start door in the exit layer distinct from the "start door" in the exit layer
#so there may be two copies of each door, one used only for exits and one used for only starts
#need to modify popualte_layers and add_path_to_layer
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

    return TW_start, TW_exit, OW_start, OW_exit

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
    
    BS_start_layer, BS_exit_layer = rooms_to_layer(B_start_rooms)
    BE_start_layer, BE_exit_layer = rooms_to_layer(B_end_rooms)
    
    BS_start_layer.graph["name"] = "BS_start_layer"
    BS_exit_layer.graph["name"] = "BS_exit_layer"
    BE_start_layer.graph["name"] = "BE_start_layer"
    BE_exit_layer.graph["name"] = "BE_exit_layer"
    
    return BS_start_layer, BS_exit_layer, BE_start_layer, BE_exit_layer

#RoomType.JOHN
def rooms_to_john_layer(all_rooms):
    JBE_start_layer, JBE_exit_layer,  J_start_layer, J_exit_layer = type_and_branch_to_layers(all_rooms, RoomType.JOHN, BranchType.END)
    
    JBE_start_layer.graph["name"] = "JBE_start_layer"
    JBE_exit_layer.graph["name"] = "JBE_exit_layer"
    J_start_layer.graph["name"] = "J_start_layer"
    J_exit_layer.graph["name"] = "J_exit_layer"
    
    return  J_start_layer, J_exit_layer, JBE_start_layer, JBE_exit_layer

#RoomType.ENTRANCE
def rooms_to_entrance_layer(all_rooms):
    EBS_start_layer, EBS_exit_layer,  E_start_layer, E_exit_layer = type_and_branch_to_layers(all_rooms, RoomType.ENTRANCE, BranchType.START)
    
    EBS_start_layer.graph["name"] = "EBS_start_layer"
    EBS_exit_layer.graph["name"] = "EBS_exit_layer"
    E_start_layer.graph["name"] = "E_start_layer"
    E_exit_layer.graph["name"] = "E_exit_layer"
    
    return E_start_layer, E_exit_layer, EBS_start_layer, EBS_exit_layer  

def type_and_branch_to_layers(all_rooms, room_type, branch_type):
    
    type_rooms = filter_rooms(all_rooms, room_type)
    type_branch_rooms = filter_rooms_by_branch(type_rooms, branch_type)
    type_rooms = filter_rooms_by_branch(type_rooms, BranchType.NONE)
    
    TBT_start_layer, TBT_exit_layer = rooms_to_layer(type_branch_rooms)
    T_start_layer, T_exit_layer = rooms_to_layer(type_rooms)
    
    return T_start_layer, T_exit_layer, TBT_start_layer, TBT_exit_layer

def filter_rooms(rooms, room_type):
    return [room for room in rooms if room.room_type == room_type]

def filter_rooms_by_branch(rooms, branch_type):
    return [room for room in rooms if room.branch_type == branch_type]
























