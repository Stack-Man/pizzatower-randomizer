#Author: Stack Man
#Date: 11/9/2026

#Run the program
from json_parse import parse_json_to_rooms_all, FILENAMES
from json_source_destination import get_source_destination_rooms
from graph_from_rooms import rooms_to_graph
from graph_flow import flow
from level_generate import generate_levels_all
from seeded_random import set_seed

from settings import TraversalMode

def generate_levels():
    set_seed(0)

    all_rooms = parse_json_to_rooms_all(FILENAMES)
    SD = get_source_destination_rooms(all_rooms)

    FG = rooms_to_graph(all_rooms, traversal_mode=TraversalMode.MATCHING_PERFECT)
    FG = flow(FG)

    #TODO: seeded randomize order of SD and FG lists

    levels = generate_levels_all(SD, FG)

    #TODO: export levels to json