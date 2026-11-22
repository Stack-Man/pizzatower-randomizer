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

#TODO: we dont make an OW bipartite graph for use in the oneway levels (ctop, war)

#TODO: main performance cost is deepcopy
#since we have to copy for every single recursion call we end up calling deepcopy on the graph a LOT
#is there a more efficient way to handle it?
#maybe if instead of making a copy for every recursion depth, we actually resupply the graph with the failed consumed rooms and paths...

#can't direcyly resupply beacuse then the list order possibly changes?
#when we take from a pathlist, we always take from the end... 

#for traverasls, we always take the first one available
#adn we don't interate over them...

#the big problem are paths we remoev not because tehy were selected but because they were part of a room that was selected
#as those are nto necessiarly at the end, so resupplying them can't be done from the back

#maybe we can try some list type that automatically orders by ID or something so they always end up in the same order?

#for traversals, we remove when it has a zero edge, though technically we shouldn't need to do that since
#we already check a traversal if it has a zero edge

#another trouble is when we add a new DB edge to a traversal's bipartite graphs,  we'll have to remove it
#we have to recheck the traversal type when we remove the readd the edge...

#these bipartite graphs are kind of problematic since we have to manage remove and adding every time 
#AND copy them for EVERY traversal AND copy EVERY node within, that might be part of why deepcopy is so unperformant




#FG has:
# * nodes:
#       * dict of destination, traversals
#           * traversals:
#               * list of Edges
#               * 3 Bipartite graphs 
# * Edges:
#        * 4 PathList
#           * List of DB paths
#           * List of NDB paths
# * Path:
#       * Associated Room
#       * Associated Edge
# * Bipartite Graph:
#       * Node Sets R/E:
#           *R: nodes representing rooms
#           *E: nodes representing edges in the traversal
#       * Edges: between R and E showing that R has a path that can be chosen for E


# Okay so our problem comes down to a few things:
# 1. Deepcopies in Recursion AND in Briding are called often and are expensive
# 2. Recursion copy is needed to revert state on step back 
# 3. Bridging copy is needed to revert state on failure after partial bridge
# 4a. during segment generation, after dump, segment was ditched but selected rooms are still removed from FG
#           AKA we remove from FG immediately before confirming the segment is used 
#           do we need to clean immediately? The traversal should alrady prevent impossible booking... perhaps we can select and wait
# 4b. not the case for SD as SDs are only removed from SD at the satrt of the next call

# Solution:
# replace deepcopies with replenishing
# 1. on room selection, do NOT immediately clean selected rooms from FG
# 2. on TRY: clean segment from SD and FG
# 3. on DUMP: replenish segment to SD and FG

# Clean:
# 1. remove segment ends from SD
# 2. for each room of each path in segment traversal
# 2b. remove that room's paths from FG
# 3. use bipartite graph to recalculate traversal type of traversals with removed paths

# Replenish:
# 1. re-add segment ends to SD 
#       (problem, we are removing and adding from a list that is actively being iterated on...)
#       perhaps we can continue to deepcopy SD since that is relatively small?
# 2. for each room of each path in segment traversal 
#       (problem, list order has changed, possibly effecting generation)
#       does this matter? We are not iterating over path lists, just taking from the back.
#       this will never cause an issue because we don't actually care which path we take from
#       a path list, we just need any of them.
# 2b. readd that room's paths to FG
# 3. use bipartite graph to recalculate traversal type of traversals with added paths


#Clean and Replenish for FG will
#1. remove need to deepcopy FG on each recursion branch
#2. remove need to deepcopy FG before room selection (failed partial selections no longer drain FG)
#3. replenish FG with rooms that were selected but later dumped after level completion from that segment fails

#NOTE: for room selection, we will need to check rooms as we pick them from the PathList, to ensure that we do not select the same room twice
#since we are no longer cleaning up the FG after each path is selected, we may encounter a path yet to be removed from the path list
#for bridge branching, we will have to remember what's in NPT when selecting PT as well, to prevent the same issue

#for bridge branching, not cleaning between branches means taht we may select a traversal that is no longer valid for that type due to path exhaustion
#or that encoutnered a double booking
#so for that case, we should perform a clean between branch generation then replneish on failure

#Deepcopy for SD because
#1. SD is small
#2. avoids modifying a list as it is being iterated on


#TODO:
#1. clean on TRY segment
#2. replenish on DUMP segment
#3. track used rooms in selection
#4. clean on TRY NPT
#5. replenish on DUMP NPT
#6. be sure to replenish TW, Branch, AND self loop properly




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