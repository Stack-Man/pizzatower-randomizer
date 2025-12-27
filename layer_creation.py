from enums import *
import networkx as nx
import node_id_objects as nio
from node_id_objects import StartExitType

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
    

def rooms_to_layer(rooms, layer_id, path_selector = lambda e: True):
    
    print(str(len(rooms)) + " rooms to layer " + str(layer_id))
    
    msg = ""
    
    for room in rooms:
        msg += ", " + str(room.name)
    
    print("rooms: " + msg)
    
    return populate_start_and_exit_layer(rooms, layer_id, path_selector)


#start/exit layers are virtual layers within a single greater layer
#each door exits twice in the layer, once in start and once in exit
#providing a way to create distinct directionality as you move through the
#layer and preventing unwanted backtracking
def populate_start_and_exit_layer(rooms, layer_id, path_selector = lambda e: True):
    layer = nx.DiGraph()
    layer_ids = [StartExitType.START, StartExitType.EXIT]

    for room in rooms:
        room_id = nio.create_room_node_id(layer_id, room.name)

        layer.add_node(room_id)
       
        for door in room.doors:
            

            #add door and connect room to door
            for layer_type_id in layer_ids:
                
                #Layer name, start/exit, room name, door letter
                door_id = nio.create_door_node_id(layer_id, layer_type_id, room.name, door.letter)
                
                layer.add_node(door_id)
                layer.add_edge(room_id, door_id)    

        #add paths between layers
        for path in room.paths:
            if path_selector(path):
                add_start_exit_path_to_layer(room_id, path, layer, layer_id)
    
    return layer

def add_start_exit_path_to_layer(room_id, path, layer, layer_id):
    
    add_one_start_exit_path_to_layer(room_id, path, path.start_door, path.exit_door, layer, layer_id)
    
    if not path.oneway:
        add_one_start_exit_path_to_layer(room_id, path, path.exit_door, path.start_door, layer, layer_id)
    
    return
    
def add_one_start_exit_path_to_layer(room_id, path, start_door, exit_door, layer, layer_id):
    #add start transition node
    #Layer name, start/exit, door type, door direction
    start_transition_id = nio.create_transition_node_id(layer_id, StartExitType.START, start_door.door_type, start_door.door_dir)
    layer.add_node(start_transition_id)
    
    #add exit transition node
    exit_transition_id = nio.create_transition_node_id((layer_id, StartExitType.EXIT, exit_door.door_type, exit_door.door_dir)
    layer.add_node(exit_transition_id)
    
    #connect start transition type to start door in start layer
    #add path as attribute to this edge
    
    #Layer name, start/exit, room name, door letter
    start_door_id = (layer_id, LAYER_START_ID, room_id, start_door.letter)
    layer.add_edge(start_transition_id, start_door_id)
    layer[start_transition_id][start_door_id][LAYER_PATH] = path
    
    #connect exit door to exit transition type to in exit layer
    exit_door_id = (layer_id, LAYER_EXIT_ID, room_id, exit_door.letter)
    layer.add_edge(exit_door_id, exit_transition_id)
    
    #connect start door in start layer to exit door in exit layer
    layer.add_edge(start_door_id, exit_door_id)
    
    return


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
    

LAYER_PATH = "path"
LAYER_DOOR = "door"
LAYER_ROOM = "room"
LAYER_TRANSITION = "transition"
LAYER_TYPE = "type"

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


#RoomType.JOHN
def rooms_to_john_layer(all_rooms):
    
    JBE_layer, J_layer = type_and_branch_to_layers(all_rooms, RoomType.JOHN, BranchType.END, "John Branch", "John")
    
    JBE_layer.graph["name"] = "John Branch"
    J_layer.graph["name"] = "John"
    
    return J_layer, JBE_layer 
    

#RoomType.ENTRANCE
def rooms_to_entrance_layer(all_rooms):
    
    EBS_layer, E_layer = type_and_branch_to_layers(all_rooms, RoomType.ENTRANCE, BranchType.START, "Entrance Branch", "Entrance")
    
    EBS_layer.graph["name"] = "Entrance Branch"
    E_layer.graph["name"] = "Entrance"
    
    return E_layer, EBS_layer
    


def type_and_branch_to_layers(all_rooms, room_type, branch_type, branch_layer_id, layer_id):
    
    type_rooms = filter_rooms(all_rooms, room_type)
    type_branch_rooms = filter_rooms_by_branch(type_rooms, branch_type)
    type_rooms = filter_rooms_by_branch(type_rooms, BranchType.NONE)
    
    TBT_layer = rooms_to_layer(type_branch_rooms, branch_layer_id)
    T_layer = rooms_to_layer(type_rooms,layer_id)
    
    return TBT_layer, T_layer
    

def filter_rooms(rooms, room_type):
    return [room for room in rooms if room.room_type == room_type]

def filter_rooms_by_branch(rooms, branch_type):
    return [room for room in rooms if room.branch_type == branch_type]
























