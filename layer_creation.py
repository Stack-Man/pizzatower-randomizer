from enums import *
import networkx as nx

#==========================================
#   Layer Creation
#==========================================
#All Rooms
#Divide into room types for different layers
def rooms_to_layers(rooms):
    
    TW_start_layer, TW_exit_layer, OW_start_layer, OW_exit_layer = rooms_to_TW_and_OW_layers(rooms)
    branch_start_layer, branch_end_layer = rooms_to_branch_layers(rooms)
    john_layer, branch_john_layer = rooms_to_john_layer(rooms)
    entrance_layer, branch_entrance_layer = rooms_to_entrance_layer(rooms)
    
    return

#RoomType.NORMAL
#Four Copies, one with and one without oneway paths
#One layer for starts one layer for exits
def rooms_to_TW_and_OW_layers(all_rooms):
    
    rooms = filter_rooms(all_rooms, RoomType.NORMAL)
    
    TW_start_layer = nx.DiGraph()
    TW_exit_layer = nx.DiGraph()
    OW_start_layer = nx.DiGraph()
    OW_exit_layer = nx.DiGraph()
    
    layers = [TW_start_layer, TW_exit_layer, OW_start_layer, OW_exit_layer]
    
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
        
        
        for path in room.paths:
            add_path_to_layers(room_id, path, OW_start_layer, OW_exit_layer)
            
            if not path.oneway:
                add_path_to_layers(room_id, path, TW_start_layer, TW_exit_layer)
            
            
    return TW_start_layer, TW_exit_layer, OW_start_layer, OW_exit_layer

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
#Two layers
def rooms_to_branch_layers(rooms):
    return

#BranchType.START or BranchType.ANY
def rooms_to_branch_start_layer(rooms):
    return

#BranchType.END or BranchType.ANY
def rooms_to_branch_end_layer(rooms):
    return

#RoomType.JOHN
def rooms_to_john_layer(rooms):
    return

#RoomType.ENTRANCE
def rooms_to_entrance_layer(rooms):
    return

def filter_rooms(rooms, room_type):
    return [room for room in rooms if room.room_type == room_type]

def filter_rooms_by_branch(rooms, branch_type):
    return [room for room in rooms if room.branch_type == branch_type]






















