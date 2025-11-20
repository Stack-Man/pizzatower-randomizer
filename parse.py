#Author: Stack Man
#Date 11/17/2025

#TODO: decide how to handle outer path creation (room to room) vs inner path creation (door to door in a room)
#how to efficinetly pick a room that has a good path out?

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

from typing import List, Dict
from constants import JSON_NAMES
from objects import Path, Room, Door
from enums import RoomType, BranchType, DoorDir, PathTime, AccessType

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

def read_json_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in: {file_path}")
    return None

def parse_room(room: Dict) -> Room:
    doors = []

    for door in room[Room.doors]:
        new_door = parse_door(door)
        doors.append(new_door)

    is_john = "pillar" in room
    is_entrance = "entrance" in room
    room_name = room[Room.name]

    branch_type = BranchType.NONE #TODO:

    #parse paths
    paths = []
    
    #for every door
    for a in range(0, len(doors)):

        door_a = doors[a]

        #handle one door rooms
        c = a if len(doors) <= 1 else a + 1
        parse_powerup(door_a, room_name)

        #for every door after that
        for b in range(c, len(doors)):

            door_b = doors[b]

            path_ab = parse_path(door_a, door_b, is_john)
            path_ba = parse_path(door_a, door_b, is_john)

            if branch_type != BranchType.START and branch_type != BranchType.END:
                branch_type = check_paths_for_branch_type(path_ab, path_ba, branch_type)
                
            if path_ab != None:
                paths.append(path_ab)
            
            #don't double add loop paths
            if path_ba != None and door_a.letter != door_b.letter:
                paths.append(path_ba)

    room_type = find_room_type(paths, is_john, is_entrance, branch_type)

    #TODO: seeded shuffle of paths

    room = Room(room_name,
                paths,
                branch_type,
                room_type)

    return room

DOOR_BRANCH = "banch"
DOOR_INITIALLY_BLOCKED = "ratblocked"
DOOR_PIZZATIMESTART = "pizzatimestart"
DOOR_NOTPIZZATIMESTART = "notpizzatimestart"
DOOR_NOTPIZZATIMEEXITONLY = "notpizzatimeexitonly"
DOOR_LOOP = "loop"

#TODO: rework path time to be start path time and exit path time
#TODO: rework Door object to be a struct with properties instead of a class
def parse_door(door: Dict) -> Door:

    letter = door.get(DOOR_LETTER)
    door_type = door.get(DOOR_TYPE)
    door_dir = door.get(DOOR_DIR)

    if door_dir == None:
        door_dir = DoorDir.NONE

    is_branch = DOOR_BRANCH in door
    initially_blocked = DOOR_INITIALLY_BLOCKED in door
    path_time = get_path_time(door)
    
    access_type = AccessType.Any

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

    is_loop = door_loop in door

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


def parse_path(start_door: Door, exit_door: Door, is_john):

    #start is exitonly or exit is startonly
    if start_door.access_type == AccessType.EXITONLY or exit_door.access_type == AccessType.STARTONLY:
        return None

    #path is notpizzatime but start door can only be exit in notpizzatime
    if start_door.if_notpizzatime_exit_only and (start_door.path_time == PathTime.NOTPIZZATIME or exit_door.path_time == PathTime.NOTPIZZATIME):
        return None

    #path time mismatch, unless it is in a john room
    if not is_john and (start_door.path_time != PathTime.BOTH or exit_door.path_time != PathTime.BOTH) and start_door.path_time != exit_door.path_time:
        return None

    path_time = PathTime.BOTH

    if not is_john:
        if start_door.path_time == PathTime.PIZZATIME or exit_door.path_time == PathTime.PIZZATIME:
            path_time = PathTime.PIZZATIME
        
        if start_door.path_time == PathTime.NOTPIZZATIME or exit_door.path_time == PathTime.NOTPIZZATIME:
            path_time = PathTime.NOTPIZZATIME
    
    is_oneway = (start_door.access_type == AccessType.STARTONLY and not start_door.initially_blocked) or (exit_door.access_type == AccessType.EXITONLY and not exit_door.initially_blocked)
    is_loop = start_door.is_loop or exit_door.is_loop

    new_path = Path(start_door, exit_door, path_time, is_oneway, is_loop)

    return new_path


#TODO:
def parse_powerup(door: Door, room_name: str):
    pass


#TODO
def check_paths_for_branch_type(path_ab: Path, path_ba: Path, current_branch_type: BranchType):
    pass


#TODO
def find_room_type(paths: List[Path], is_john: bool, is_entrance: bool, current_branch_type: BranchType):
    pass
