#Author: Stack Man
#Date: 11/12/2026

from level_generate_recursive import generate_levels_recursive_all
from level_objects import Level
from json_parse import FILENAMES
from json_objects import Room

from level_bridge import bridge_branch_room_room

from json_parse import parse_json_to_rooms_all, FILENAMES
from json_source_destination import get_source_destination_rooms
from graph_from_rooms import rooms_to_graph
from graph_flow import flow
from level_generate_recursive import generate_levels_recursive_all
from seeded_random import set_seed
from graph_collapse import collapse_all_nodes_and_edges

from settings import TraversalMode

from perf_counter import print_perf, print_perf_type, PerfType

import log_config
import logging as log

to_test = FILENAMES

def get_SD_FG_rooms(fn):
    all_rooms = parse_json_to_rooms_all(fn)
    SD = get_source_destination_rooms(all_rooms)

    FG = rooms_to_graph(all_rooms, traversal_mode=TraversalMode.MATCHING_PERFECT)
    FG = collapse_all_nodes_and_edges(FG)
    FG = flow(FG)

    #TODO: seeded randomize order of SD and FG lists

    return SD, FG, all_rooms

def test_generate():
    SD, FG, _ = get_SD_FG_rooms(to_test) 
    print_perf_type(PerfType.JSON)
    print_perf_type(PerfType.GRAPH)
    print_perf_type(PerfType.FLOW)
    levels, new_SD, new_FG = generate_levels_recursive_all(SD, FG)

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

def print_room_by_name(room_name: str):
    all_rooms = parse_json_to_rooms_all(FILENAMES)

    for room in all_rooms:
        if (room.name == room_name):
            room.print_stats()

            for path in room.paths:
                path.print_stats_extended()

            return

test_generate()
print_perf()
#test_bridge_branch_room_room_by_name("sewer_1", "chateau_5")
#print_room_by_name("chateau_5")