#Author: Stack Man
#Date: 11/9/2026

#Run the program
from json_parse import parse_json_to_rooms_all, FILENAMES
from json_source_destination import get_source_destination_rooms
from graph_create import rooms_to_graph
from graph_flow import flow
from level_generate_recursive import generate_levels_recursive_all
from seeded_random import set_seed
from graph_collapse import collapse_all_nodes_and_edges
from level_grow import grow_levels

from settings import TraversalMode,  GRAPH_TRAVERSAL_MODE, get_growth_settings

#TODO: Flow got slower, because of changes to graph_impossible_booking.py?
#TODO: traversal rechecking is slow AF

def get_SD_FG_rooms(fn: list[str], traversal_mode : TraversalMode):

    all_rooms = parse_json_to_rooms_all(fn)
    SD = get_source_destination_rooms(all_rooms)

    FG = rooms_to_graph(all_rooms, traversal_mode=traversal_mode)
    FG = collapse_all_nodes_and_edges(FG)
    FG = flow(FG)

    #TODO: seeded randomize order of SD and FG lists

    return SD, FG, all_rooms
    

def generate_levels():
    set_seed(0)
    
    SD, FG, rooms = get_SD_FG_rooms(FILENAMES, GRAPH_TRAVERSAL_MODE)

    levels, SD2, FG2 = generate_levels_recursive_all(SD, FG)
    levels = grow_levels(levels, FG2, get_growth_settings())

    #TODO: grow size of levels

    #TODO: export levels to json