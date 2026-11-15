#Author: Stack Man
#Date: 11/12/2026

from level_generate_recursive import generate_levels_recursive_all
from main import get_SD_FG_rooms
from level_objects import Level
from json_parse import FILENAMES
from json_objects import Room

from level_bridge import bridge_branch_room_room

to_test = ["crustcove"]

def test_generate():
    SD, FG, _ = get_SD_FG_rooms(to_test) 
    levels = generate_levels_recursive_all(SD, FG)

    print_levels(levels)

def print_levels(levels: list[Level]):

    for level in levels:
        print(f"Level: {level.name}")
        print(f"{level}")

def room_by_name(rooms: list[Room], A: str):
    for room in rooms:
        if (room.name == A):
            return room

    raise ValueError(f"No room of name {A} in rooms!")

def test_bridge_branch_room_room_by_name(A: str, B: str):
    SD, FG, all_rooms = get_SD_FG_rooms(to_test) 
    room_A = room_by_name(all_rooms, A)
    room_B = room_by_name(all_rooms, B)

    for branch in bridge_branch_room_room(room_A, room_B, FG):
        print(f"{branch}")
    

test_generate()
#test_bridge_branch_room_room_by_name("graveyard_3", "graveyard_5c")