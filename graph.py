from json_keys import *
import networkx as nx
from enums import get_dir, get_path_time, flip_dir

#==========================================
# Params:
#   G: graph containing all current doors and transitions
#   doors: dict containing info of door (TODO: parse as Door object first instead?)
#   room_title: name of room the doors are from
#==========================================
def doors_to_nodes(G, doors, room_title):
    transition_names = []

    #======================================
    # Create nodes for all doors in a room
    # And edges between doors and transitions
    #======================================
    for door in doors:
        
        main_dir = get_dir(door) 
        transition_title = door[DOOR_TYPE] + "_" + str(main_dir)
        
        #Add new Transition node
        if transition_title not in G:
            G.add_node(transition_title)
            transition_names.append(transition_title)
        
        #Add new Door node for this room
        door_letter = door[DOOR_LETTER]
        door_title = room_title + "_" + door_letter
        
        G.add_node(door_title)
        G.add_edge(room_title, door_title)#used just to associate doors to rooms
        
        #TODO: consider pizzatimestart, ratblocked, and other special params
        
        exit_only = DOOR_EXIT_ONLY in door
        start_only = DOOR_START_ONLY in door
        
        path_time = get_path_time(door)
        
        exit_dir = get_dir(door)
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
    return G