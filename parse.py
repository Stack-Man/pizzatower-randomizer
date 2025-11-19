#Author: Stack Man
#Date 11/17/2025

"""
Read an input .json file and output a graph
"""

"""
Every Room, its doors, and each type of Transtion are represented as nodes in a graph.

Room: 
    A single room instance
    * name

Door:
    A specific transition in a room
    * letter

Room-Door Edge:
    A directional edge that implies an exit (room > door) or a start (room < door)
    * Time: [Any/Pizzatime/NotPizzatime]
    * Direction: [Any/Left/Right/Up/Down]

Transition:
    A type of transition
    * type

Door-Transition Edge:
    A bidirectional edge that associates doors with each 
    other, allowing traversal between rooms using a 
    (room - door - transition - door - room) pattern

Transition-Transition Edge:
    Temporary Edges added when randomizer mode allows cross-type transitions
"""

"""
Formatting of the JSON and description of its parameters:
#TODO
"""

import json
import networkx as nx
from enums import PathTime, DoorDir

ROOMS = "rooms"
ROOM_TITLE = "title"
ROOM_DOORS = "doors"

DOOR_TYPE = "type"
DOOR_LETTER = "letter"

DOOR_EXIT_ONLY = "exitonly"
DOOR_START_ONLY = "startonly"

def read_json(filename):
    #try:
    with open(filename, "r") as f:
        file = json.load(f)
        print("JSON data loaded successfully:")
        
        #TODO: repeated parsing then joining of transitions with all transition names
        
        parsed, new_transitions = parse_json(file)
        return join_transitions(parsed, new_transitions)
            
    #except Exception as e:
        #print(f"Error: {e}")

#TODO:
#Parse special parameters (startonly, ratblocked)
#Parse branch rooms separately (different graph for branch start/branch exit?)
#   Branch room detection
#   Separate graphs and switch between or should I mark edges with branch info?
#Mark nodes as door/room/transition

def parse_json(data):
    G = nx.DiGraph()
    transition_names = []

    for room in data[ROOMS]:
        room_title = room[ROOM_TITLE]

        doors = room.get(ROOM_DOORS)
        
        #skip rooms with no doors (secrets)
        if doors is None:
            continue
        else:
            G.add_node(room_title)
        
        for door in doors:
            
            main_dir = get_dir(door)
            
            transition_type = door[DOOR_TYPE] + "_" + str(main_dir)
            
            #Add new Transition node
            if transition_type not in G:
                G.add_node(transition_type)
                transition_names.append(transition_type)
            
            #Add new Door node for this room
            door_letter = door[DOOR_LETTER]
            door_node_index = room_title + "_" + door_letter
            
            G.add_node(door_node_index)
            
            #TODO: consider pizzatimestart, ratblocked, and other special params
            
            exit_only = DOOR_EXIT_ONLY in door
            start_only = DOOR_START_ONLY in door
            
            path_time = get_path_time(door)
            
            exit_dir = get_dir(door)
            start_dir = flip_dir(exit_dir)
            
            #room - door (exit)
            if not start_only:
                G.add_edge(room_title, door_node_index)
                G[room_title][door_node_index]["time"] = path_time
                G[room_title][door_node_index]["dir"] = exit_dir
                
            #room - door (start)
            if not exit_only:
                G.add_edge(door_node_index, room_title)
                G[door_node_index][room_title]["time"] = path_time
                G[door_node_index][room_title]["dir"] = flip_dir
                
            
            #door - transition and transition - door
            G.add_edge(door_node_index, transition_type)
            G.add_edge(transition_type, door_node_index)
        
    return G, transition_names

JOIN_TRANSITION_NAMES = ["horizontal", "vertical", "box"]

def join_transitions(G, all_transitions):

    #MODE: matching perfect
    #Match transitions with the same type and consistent directions
    for name in JOIN_TRANSITION_NAMES:
        
        nodes_to_join = []
        
        for node in G.nodes():
            
            print(str(node) + " has ? " + str(name))
        
            if name in str(node) and str(node) in all_transitions:
                nodes_to_join.append(node)
                
        for node_a in nodes_to_join:
            for node_b in nodes_to_join:
                if node_a is not node_b:
                    G.add_edge(node_a, node_b)
                    G.add_edge(node_b, node_a)
    
    #MODE: matching directional
    #Match transitions that have consistent directions, but possibly different types
    
    #MODE: arbitrary no turnarounds
    #Match transitions in any way, but don't allow left/left, right/right, up/up, or down/down
    
    #MODE: arbitrary no restrictions
    #Match transitions in any way
    
    return G

DOOR_PIZZATIME = "pizzatime"
DOOR_NOTPIZZATIME = "notpizzatime"

def get_path_time(door):
    if (DOOR_PIZZATIME in door):
        return PathTime.PIZZATIME
    elif (DOOR_NOTPIZZATIME in door):
        return PathTime.NOTPIZZATIME
    else:
        return PathTime.BOTH

DOOR_DIR = "dir"

def get_dir(door):
    door_dir = door.get(DOOR_DIR)
    
    if door_dir is None:
        return DoorDir.NONE
    elif door_dir == "up":
        return DoorDir.UP
    elif door_dir == "down":
        return DoorDir.DOWN
    elif door_dir == "left":
        return DoorDir.LEFT
    elif door_dir == "right":
        return DoorDir.RIGHT
    else:
        return DoorDir.ANY

def flip_dir(door_dir):
    if door_dir == DoorDir.UP:
        return DoorDir.DOWN
    elif door_dir == DoorDir.DOWN:
        return DoorDir.UP
    elif door_dir == DoorDir.LEFT:
        return DoorDir.RIGHT
    elif door_dir == DoorDir.RIGHT:
        return DoorDir.LEFT
    else:
        return dir

