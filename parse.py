#Author: Stack Man
#Date 11/17/2025


"""
Read an input .json file and output a graph
"""

"""
Nodes in the graph represent Room, Doors, Tnransitions, and Paths
Should paths be their own node or just an edge between doors?

Room: 
    A single room instance. Contains one way edges to each of its doors
    * name

Door:
    A specific transition in a room
    * letter
    
Path:
    A directional edge between Doors in a Room.

Transition:
    A type of transition
    * type

Door-Transition Edge:
    A directional edge that associates doors with each 
    other, allowing traversal between rooms using a 
    (room - door - transition - door - room) pattern
    Implies a start (transition > door) or an exit (door > transition)

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
from graph import doors_to_nodes, paths_to_nodes
from json_keys import * 
from enums import get_path_time, get_dir, flip_dir

#============================================
#  JSON IO 
#============================================

def parse_level_jsons():
    rooms = []

    for json_name in JSON_NAMES:
        dir = "/json/" + json_name + ".json"
        data = read_json_file(dir)
        
        if data != None:
            for room in data["rooms"]:
                new_room = parse_room(room)
                rooms.append(new_room)

    #TODO: seeded shuffle of rooms
    return rooms

def read_json(filename):
    #try:
    with open(filename, "r") as f:
        file = json.load(f)
        print("JSON data loaded successfully:")
        
        #TODO: repeated parsing then joining of transitions with all transition names
        
        parsed, new_transitions = parse_json_to_graph(file)
        
        print(f" new transitions from parse json to graph: {new_transitions}")
        
        return join_transitions(parsed, new_transitions)
            
    #except Exception as e:
        #print(f"Error: {e}")

#TODO:
#Parse special parameters (startonly, ratblocked)
#Parse branch rooms separately (different graph for branch start/branch exit?)
#   Branch room detection
#   Separate graphs and switch between or should I mark edges with branch info?
#Mark nodes as door/room/transition
#==================================================
# JSON to Graph
#==================================================
def parse_json_to_graph(data):
    G = nx.DiGraph()
    transition_names = []

    for room in data[ROOMS]:
        doors = parse_doors(room)
        
        #TODO: parse room data
        room = parse_room(room)
        room_title = room.name
        is_john = room.room_type == RoomType.JOHN
        
        #skip rooms with no doors (secrets)
        if doors is None:
            continue
        else:
            G.add_node(room_title)

        #Add doors, new transitions, and Door-Transition edges to G
        G, new_transition_names = doors_to_nodes(G, doors, room_title)
        transition_names.extend(new_transition_names)
        
        #TODO: pass room object instead of two params
        #Find Paths
        paths = parse_paths(doors, is_john = is_john, room_name = room_title)
        
        #Add Door-Door edges to G
        G = paths_to_nodes(G, paths, room_title)
        
    return G, transition_names

JOIN_TRANSITION_NAMES = ["horizontal", "vertical", "box"]

def join_transitions(G, all_transitions):
    #MODE: matching perfect
    #Match transitions with the same type and consistent directions
    print(f" all transitions inside join transitions: {all_transitions}")
    
    for name in JOIN_TRANSITION_NAMES:
        
        print(f"    name to check: {name}")
        
        nodes_to_join = []
        
        for node in G.nodes():
        
            #print(f"        {node}")
        
            if name in str(node) and str(node) in all_transitions:
                nodes_to_join.append(node)
                print(f"    node to join: {node}")
                
        for node_a in nodes_to_join:
            for node_b in nodes_to_join:
                if node_a is not node_b:
                    G.add_edge(node_a, node_b)
                    G.add_edge(node_b, node_a)
    
    #MODE: matching directional
    #Match transitions that have consistent directions, but possibly different types
    #TODO:
    
    #MODE: arbitrary no turnarounds
    #Match transitions in any way, but don't allow left/left, right/right, up/up, or down/down
    #TODO:
    
    #MODE: arbitrary no restrictions
    #Match transitions in any way
    #TODO:
    
    return G


from typing import List, Dict
from constants import JSON_NAMES
from objects import Path, Room, Door
from enums import RoomType, BranchType, DoorDir, PathTime, AccessType

#=================================
# Parse Dict to Objects
#=================================

def parse_room(room: Dict) -> Room:
    doors = []

    if Room.doors in room:
        for door in room[Room.doors]:
            new_door = parse_door(door)
            doors.append(new_door)

    is_john = "pillar" in room
    is_entrance = "entrance" in room
    room_name = room[Room.name]

    branch_type = BranchType.NONE #TODO:

    #parse paths
    paths = parse_paths(doors, is_john, room_name)

    room_type = find_room_type(paths, is_john, is_entrance, branch_type)

    #TODO: seeded shuffle of paths

    room = Room(room_name,
                paths,
                branch_type,
                room_type)

    return room


def parse_doors(room):
    if ROOM_DOORS not in room:
        return None

    doors = []

    for door in room[ROOM_DOORS]:
        new_door = parse_door(door)
        doors.append(new_door)
        
    return doors

#TODO: rework path time to be start path time and exit path time
def parse_door(door: Dict) -> Door:

    letter = door.get(DOOR_LETTER)
    door_type = door.get(DOOR_TYPE)
    door_dir = door.get(DOOR_DIR)

    if door_dir == None:
        door_dir = DoorDir.NONE

    is_branch = DOOR_BRANCH in door
    initially_blocked = DOOR_INITIALLY_BLOCKED in door
    path_time = get_path_time(door)
    
    access_type = AccessType.ANY

    if DOOR_START_ONLY in door:
        access_type = AccessType.STARTONLY
    elif DOOR_EXIT_ONLY in door:
        access_type = AccessType.EXITONLY
    
    #if used as a start, must be this time
    path_time_if_start = PathTime.BOTH

    if DOOR_PIZZATIMESTART in door:
        path_time_if_start = PathTime.PIZZATIME
    elif DOOR_NOTPIZZATIMESTART in door:
        path_time_if_start = PathTime.NOTPIZZATIME

    #if notpizzatime, must be used as an exit
    if_notpizzatime_exit_only = DOOR_NOTPIZZATIMEEXITONLY in door

    is_loop = DOOR_LOOP in door

    door = Door(letter,
                door_type,
                door_dir,
                is_branch,
                initially_blocked,
                path_time,
                access_type,
                path_time_if_start,
                if_notpizzatime_exit_only,
                is_loop)

    return door


def parse_paths(doors, is_john, room_name):
    branch_type = BranchType.NONE #TODO: moved from parse_room temporarily

    #parse paths
    paths = []
    
    #for every door
    for a in range(0, len(doors)):

        door_a = doors[a]

        #handle one door rooms
        c = a if len(doors) <= 1 else a + 1
        
        #TODO: implement powerup
        #parse_powerup(door_a, room_name)

        #for every door after that
        for b in range(c, len(doors)):

            door_b = doors[b]

            path_ab = parse_path(door_a, door_b, is_john)
            path_ba = parse_path(door_b, door_a, is_john)

            if branch_type != BranchType.START and branch_type != BranchType.END:
                branch_type = check_paths_for_branch_type(path_ab, path_ba, branch_type)
                
            if path_ab != None:
                paths.append(path_ab)
            
            #don't double add loop paths
            if path_ba != None and door_a.letter != door_b.letter:
                paths.append(path_ba)
    
    return paths

def parse_path(start_door, exit_door, is_john):

    #start is exitonly or exit is startonly
    if start_door.access_type == AccessType.EXITONLY or exit_door.access_type == AccessType.STARTONLY:
        return None

    #path time mismatch, unless it is in a john room
    #path times of start and exit must match or at least one is BOTH
    if not is_john and (start_door.start_path_time is not PathTime.BOTH or exit_door.exit_path_time is not PathTime.BOTH) and start_door.start_path_time is not exit_door.exit_path_time:
        return None
    
    #Determine which path_time to set the path
    path_time = PathTime.BOTH

    if not is_john:
        if start_door.start_path_time == PathTime.PIZZATIME or exit_door.exit_path_time == PathTime.PIZZATIME:
            path_time = PathTime.PIZZATIME
        
        if start_door.start_path_time == PathTime.NOTPIZZATIME or exit_door.exit_path_time == PathTime.NOTPIZZATIME:
            path_time = PathTime.NOTPIZZATIME
    
    #oneway = start or exit only but not initially blocked
    is_oneway = (start_door.access_type == AccessType.STARTONLY and not start_door.initially_blocked) or (exit_door.access_type == AccessType.EXITONLY and not exit_door.initially_blocked)
    
    is_loop = start_door.is_loop or exit_door.is_loop

    new_path = Path(start_door, exit_door, path_time, is_oneway, is_loop)

    return new_path


#TODO:
def parse_powerup(door: Door, room_name: str):
    pass


#TODO:
def find_room_branch_type(room):
    pass

#TODO
def check_paths_for_branch_type(path_ab: Path, path_ba: Path, current_branch_type: BranchType):
    pass


#TODO
def find_room_type(paths: List[Path], is_john: bool, is_entrance: bool, current_branch_type: BranchType):
    pass
