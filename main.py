#Author: Stack Man
#Date: 11/9/2026

#Run the program
from json_parse import parse_json_to_rooms_all, FILENAMES
from json_source_destination import get_source_destination_rooms
from graph_from_rooms import rooms_to_graph
from graph_flow import flow
from level_generate_recursive import generate_levels_recursive_all
from seeded_random import set_seed
from graph_collapse import collapse_all_nodes_and_edges

from settings import TraversalMode,  GRAPH_TRAVERSAL_MODE

#TODO: war and ctop need special creation logic and exit types with OW segment creation

#TODO: only 9 levels generated, even though it should be around 20 (and all levels can generate individually)
#happens even if we use ARBITRARY NO TURNAROUNDS, which should have more than enough paths to match
#ther may be some logic preventing thed oor nodes from being matchd together?

def get_SD_FG_rooms(fn):
    set_seed(0)
    
    all_rooms = parse_json_to_rooms_all(fn)
    SD = get_source_destination_rooms(all_rooms)

    FG = rooms_to_graph(all_rooms, traversal_mode=GRAPH_TRAVERSAL_MODE)
    FG = collapse_all_nodes_and_edges(FG)
    FG = flow(FG)

    #TODO: seeded randomize order of SD and FG lists

    return SD, FG, all_rooms
    

def generate_levels():
    return
    SD, FG = get_SD_FG(FILENAMES)

    levels = generate_levels_recursive_all(SD, FG)

    #TODO: grow size of levels

    #TODO: export levels to json