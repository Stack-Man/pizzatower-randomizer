import json
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


def parse_door(door: Dict) -> Door:

    letter = door.get("letter")
    door_type = door.get("type")

    door_dir = door.get("dir")

    if door_dir == None:
        door_dir = DoorDir.NONE

    is_branch = "branch" in door
    initially_blocked = "ratblocked" in door

    path_time = PathTime.BOTH

    if "notpizzatime" in door:
        path_time = PathTime.NOTPIZZATIME
    elif "pizzatime" in door:
        path_time = PathTime.PIZZATIME
    
    access_type = AccessType.Any

    if "startonly" in door:
        access_type = AccessType.STARTONLY
    elif "exitonly" in door:
        access_type = AccessType.EXITONLY
    
    #if used as a start, must be this time
    path_time_if_start = PathTime.BOTH

    if "pizzatimestart" in door:
        path_time_if_start = PathTime.PIZZATIME
    elif "notpizzatimestart" in door:
        path_time_if_start = PathTime.NOTPIZZATIME

    #if notpizzatime, must be used as an exit
    if_notpizzatime_exit_only = "notpizzatimeexitonly" in door

    is_loop = "loop" in door

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