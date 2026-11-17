#Author: Stack Man
#Date: 11/16/2026

#Modify some rooms with special exceptiosn

from json_objects import Room, Door, Path, SelfLoop
from enums import RoomType, BranchType, PathTime, DoorDir, DoorType, AccessType

import logging as log
from colors import WARNING, RESET

def modify_room(room: Room, name: str):
    match name:
        case "minigolf_8":
            return minigolf_8(room)
        case _:
            raise NotImplementedError(f"Room {room} is not implemented")

def minigolf_8(room: Room):

    #treat minigolf_8 as a J room
    #modify so that E is the only path and add a SelfLoop 
    
    log.warning("%sminigolf_8 does not have SelfLoop logic fully implemented!%s", WARNING, RESET)

    door_E = Door(
        "E", 
        DoorType.DOOR, 
        DoorDir.NONE, 
        False, False, False, False, 
        PathTime.BOTH, 
        AccessType.ANY, 
        path_time_if_start=PathTime.NOTPIZZATIME, 
        if_notpizzatime_exit_only=False,
        is_loop=False)

    door_A = Door(
        "A", 
        DoorType.DOOR, 
        DoorDir.NONE,
        False, False, False, False,
        PathTime.PIZZATIME,
        AccessType.EXITONLY,
        path_time_if_start=PathTime.PIZZATIME,
        if_notpizzatime_exit_only=True,
        is_loop=False)

    door_B = Door(
        "B", 
        DoorType.BOX, 
        DoorDir.UP,
        False, False, False, False,
        PathTime.PIZZATIME,
        AccessType.ANY,
        path_time_if_start=PathTime.PIZZATIME,
        if_notpizzatime_exit_only=False,
        is_loop=False)

    doors = [door_E, door_A, door_B]


    path_EE = Path(door_E, door_E, True, False)

    paths = [path_EE]

    result = Room("minigolf_8", doors, paths, True, False, False, False, True)

    result.room_type = RoomType.JOHN
    result.branch_type = BranchType.NONE

    path_EA = Path(door_E, door_A, True, False)
    path_BE = Path(door_B, door_E, False, True)

    result.self_loop = SelfLoop(path_EA, path_BE, PathTime.PIZZATIME, True)
    
    return result