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

#TODO: if i want to seriously cut down on the amount of generation itme, I ened to improve
#traversal type updating

#there are 28k traversals, updating thousands every time an edge is updated is no bueno
#and every single one of these traversals has three bipartite graphs to maintain to help check its impossible booking status and traversal type

#there may be repeated connected components across these traversals

#every traversal has a set of connected components

#when we update an edge we either:
#So we may

#1. Update. Add or remove rooms.
#May connect or disconnect two connected components due to room removal

#2. Add or Remove Edge (DB status changed)
#May create a unique CC, removing others through modification or combination

#one major flaw of the current set up is that we update EVERY traversal even though we are only using a fraction of them for generation...

#what if we delay updating a traversal and its BG until we actually want to use it?

#this may still process a lot since we may have a lot of failed traversals to check until we get a successful one, but may be better if we can avoid 
#doing unnecessary traversal checks

#consider this:
#we either
#1. Always update every affected traversal
#2. Sometimes update only some of the affected traversals

#it can't get worse than updating all of them

#So our new strategy becomes:
#1. maintain a list of all affected edges
#2. whenever we try a traversal, check if that traversal contains any affected edge
#3. get a list of all affected edges on that traversal
#4. perform the updates and find the new traversal type

#TODO: could also add threading to traversal updating... since no traversal depends on the other

#TODO: implement FastGarph as replacement to bipartite networkx graphs for better performance


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