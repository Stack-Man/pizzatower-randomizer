#Author: Stack Man
#Date: 11/18/2026

from json_parse import parse_json_to_rooms_all
from json_source_destination import get_source_destination_rooms
from graph_create import rooms_to_graph
from graph_flow import flow
from level_generate_recursive import generate_levels_recursive_all
from graph_collapse import collapse_all_nodes_and_edges
from level_grow import grow_levels
from level_randomize import randomize_SD_FG, set_seed

from settings import TraversalMode, GrowthMode

def get_SD_FG(fn: list[str], traversal_mode : TraversalMode):

    all_rooms = parse_json_to_rooms_all(fn)
    SD = get_source_destination_rooms(all_rooms)

    FG = rooms_to_graph(all_rooms, traversal_mode=traversal_mode)
    FG = collapse_all_nodes_and_edges(FG)
    FG = flow(FG)

    #randomize lists in place
    randomize_SD_FG(SD, FG)

    return SD, FG

def generate_base_levels(fn: list[str], traversal_mode : TraversalMode, seed: int = 0):
    set_seed(seed)
    
    SD, FG = get_SD_FG(fn, traversal_mode)

    levels, SD2, FG2 = generate_levels_recursive_all(SD, FG)

    return levels, FG2

def generate_levels(fn: list[str], traversal_mode : TraversalMode, growth_mode: GrowthMode, seed: int = 0):
    levels, FG = generate_base_levels(fn, traversal_mode, seed)
    levels = grow_levels(levels, FG, growth_mode)

    return levels