from json_keys import *
import networkx as nx
from enums import *

#==========================================
# Params:
#   G: graph containing all current doors and transitions
#   doors: dict containing info of doors
#   room_title: name of room the doors are from
#==========================================
#TODO: switch to using door objects
def doors_to_nodes(G, doors, room_title):
    transition_names = []

    #======================================
    # Create nodes for all doors in a room
    # And edges between doors and transitions
    #======================================
    for door in doors:
        
        exit_dir = door.door_dir
        transition_title = door.door_type + "_" + str(exit_dir)
        
        #Add new Transition node
        if transition_title not in G:
            G.add_node(transition_title)
            transition_names.append(transition_title)
        
        #Add new Door node for this room
        door_letter = door.letter
        door_title = room_title + "_" + door_letter
        
        G.add_node(door_title)
        G.add_edge(room_title, door_title)#used just to associate doors to rooms
        
        #TODO: consider pizzatimestart, ratblocked, and other special params
        
        exit_only = door.access_type == AccessType.EXITONLY
        start_only = door.access_type == AccessType.STARTONLY
        
        path_time = door.path_time

        start_dir = flip_dir(exit_dir)
        
        #transition > door (start)
        if not exit_only:
            G.add_edge(transition_title, door_title)
            G[transition_title][door_title]["time"] = path_time
            G[transition_title][door_title]["dir"] = exit_dir
            
        #door > transition (exit)
        if not start_only:
            G.add_edge(door_title, transition_title)
            G[door_title][transition_title]["time"] = path_time
            G[door_title][transition_title]["dir"] = flip_dir
    
    return G, transition_names


def paths_to_nodes(G, paths, room_title):
    #Get path objects
    #add edges between nodes in G based on the paths
    #add information to each edge
    
    print("Paths of: " + str(room_title))
    
    for path in paths:
        
        #TODO: consistent func for constructing the node name
        door_a = room_title + "_" + str(path.start_door.letter)
        door_b = room_title + "_" + str(path.exit_door.letter)
        
        print("     new edge: " + door_a + ", " + door_b)
        
        G.add_edge(door_a, door_b)
        
        if not path.oneway:
            G.add_edge(door_b, door_a)
        
        #TODO: add other info to the edge
    
    return G