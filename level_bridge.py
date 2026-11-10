#Author: Stack Man
#Date: 11/9/2026

#Bridge two rooms using the Flow Graph and select their rooms

from objects import Room
from colors import WARNING, RESET
from level_objects import TwowaySegment, BranchSegment, RoomSelection

from enums import PathTime

def bridge_twoway(start_room: Room, end_room: Room, FG):
    print(f"{WARNING}generate_twoway() in level_generate.py not implemented{RESET}")
    return TwowaySegment(start_room, end_room, RoomSelection([]))

def bridge_branch(start_room: Room, end_room: Room, FG):
    print(f"{WARNING}generate_branch() in level_generate.py not implemented{RESET}")

    NPT = bridge_oneway_from_branch(start_room, end_room, PathTime.NOTPIZZATIME, FG)
    PT = bridge_oneway_from_branch(end_room, start_room, PathTime.PIZZATIME, FG)

    return BranchSegment(start_room, end_room, PT, NPT)

def bridge_oneway_from_branch(start_room: Room, end_room: Room, path_time: PathTime, FG):
    print(f"{WARNING}generate_oneway_from_branch() in level_generate.py not implemented{RESET}")
    return RoomSelection([])