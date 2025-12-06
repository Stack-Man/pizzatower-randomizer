from json_keys import *
import networkx as nx
from enums import *

#==========================================
# Params:
#   G: graph containing all current doors and transitions
#   doors: list of door objects
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
        
        transition_title = door.door_type + "_" + str(door.door_dir)
        
        #Add new Transition node
        if transition_title not in G:
            G.add_node(transition_title)
            G.nodes[transition_title][NODE_TRANSITION] = True
            transition_names.append(transition_title)
        
        #Add new Door node for this room
        door_letter = door.letter
        door_title = get_door_title(room_title, door_letter)
        
        G.add_node(door_title)
        G.nodes[door_title][NODE_DOOR] = door
        G.nodes[door_title][NODE_ROOM_TITLE] = room_title
        G.add_edge(room_title, door_title)#used just to associate doors to rooms
        
        #Create transition - door edges
        exit_only = door.access_type == AccessType.EXITONLY
        start_only = door.access_type == AccessType.STARTONLY
     
        #transition > door (start)
        if not exit_only:
            G.add_edge(transition_title, door_title)
            
        #door > transition (exit)
        if not start_only:
            G.add_edge(door_title, transition_title)
    
    return G, transition_names

#==========================================
# Params:
#   G: graph containing all current doors and transitions
#   paths: list of path objects
#   room_title: name of room the paths are in
#==========================================
def paths_to_nodes(G, paths, room_title):

    for path in paths:
    
        door_a = get_door_title(room_title, path.start_door.letter)
        door_b = get_door_title(room_title, path.exit_door.letter)

        G.add_edge(door_a, door_b)
        G[door_a][door_b][NODE_PATH] = path
        
        #The opposite path exists as a separate object, 
        #so dont add it manually here
        
    return G

def get_door_title(room_title, letter):
    return room_title + "_" + str(letter)