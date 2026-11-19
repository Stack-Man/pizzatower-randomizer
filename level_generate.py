#Author: Stack Man
#Date: 11/18/2026

from json_parse import parse_json_to_rooms_all, FILENAMES
from json_source_destination import get_source_destination_rooms
from graph_from_rooms import rooms_to_graph
from graph_flow import flow
from level_generate_recursive import generate_levels_recursive_all
from graph_collapse import collapse_all_nodes_and_edges

from settings import TraversalMode,  GRAPH_TRAVERSAL_MODE

def get_SD_FG_rooms(fn: list[str], traversal_mode : TraversalMode):

    all_rooms = parse_json_to_rooms_all(fn)
    SD = get_source_destination_rooms(all_rooms)

    FG = rooms_to_graph(all_rooms, traversal_mode=traversal_mode)
    FG = collapse_all_nodes_and_edges(FG)
    FG = flow(FG)

    #TODO: seeded randomize order of SD and FG lists

    return SD, FG, all_rooms
    

def generate_levels(fn: list[str], traversal_mode : TraversalMode):
    SD, FG, rooms = get_SD_FG_rooms(fn, traversal_mode)

    levels, SD2, FG2 = generate_levels_recursive_all(SD, FG)

    return levels, FG2