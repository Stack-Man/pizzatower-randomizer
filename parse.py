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

    paths = parse_paths(doors)

    branch_type = BranchType.NONE #TODO:
    room_type = RoomType.NORMAL #TODO

    room = Room(room[Room.name],
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

    door = Door(letter,
                door_type,
                door_dir,
                is_branch,
                initially_blocked,
                path_time,
                access_type,
                path_time_if_start,
                if_notpizzatime_exit_only)

    return door

def parse_paths(doors: List[Door]) -> List[Path]:
    return [Path()]