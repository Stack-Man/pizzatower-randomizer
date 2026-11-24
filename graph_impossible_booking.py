#Author: Stack Man
#Date: 11/6/2926

#Create a maintain a bipartite graph where nodes are DB Rooms and DB Edges
#For any disconnected set in the graph, if R < E, the booking is impossible
#If R >= E, selection must occur from the E with the fewest edges first to avoid an impossible booking

#A separate bipartite graph is created for TW, PT, and NPT since the availability 
#of rooms for the same edge changes with Traversal Time

#Bipartite
#TW: for ONLY TW path, only check paths from TW
#PT: for PT/OW/TW
#NPT: for NPT/OW/TW

#If all path lists for a type contain only DB rooms, add that edge to the bipartite graph for that type

from graph_objects import PathEdge, PathList, BipartiteGraph, EdgeTraversal
from enums import TraversalType

from colors import ERROR, RESET, CAUTION 
import logging as log

#These first two functions are used during traversal construction to check traversal type
#as we create the traversal, allowing us to terminate invalid traversals
#bipartite_TW/PT/NPT: A bipartite graph constructed from the edge traversal up to this point
#traversal_type: priority traversal type accounting for a pathlist in edge being empty
#edge: An edge which might be DB
def add_to_bipartite_graph(bipartite_TW: BipartiteGraph, bipartite_PT: BipartiteGraph, bipartite_NPT: BipartiteGraph, traversal_type: TraversalType, edge: PathEdge):
    #check if type is already impossible or meets impossible booking reqs
    #TW = not OW, PT or NPT
    has_match_TW = (traversal_type != TraversalType.ANY or 
                    add_and_check_for_matching(bipartite_TW, edge, [edge.TW]))

    #PT = ANY PT or OW, but not NPT
    has_match_PT = (traversal_type == TraversalType.NOTPIZZATIME or 
                    add_and_check_for_matching(bipartite_PT, edge, [edge.TW, edge.OW, edge.PT]))

    #NPT = AnNY NPT or OW but not PT
    has_match_NPT = (traversal_type == TraversalType.PIZZATIME or 
                     add_and_check_for_matching(bipartite_NPT, edge, [edge.TW, edge.OW, edge.NPT]))

    #no need to make an OW bipartite graph as there is never a timeless OW path needed
    #(CTOP is PT and WAR is NPT) 
    #OW is simply a generic "both PT and NPT can work"

    new_traversal_type : TraversalType = get_traversal_type_from_possible_matchings(has_match_TW, has_match_PT, has_match_NPT)

    return new_traversal_type

def add_and_check_for_matching(BG: BipartiteGraph, edge: PathEdge, path_lists: list[PathList]):
    added = BG.add_edge_if_DB(edge, path_lists)

    if (added):
        return BG.check_for_valid_matching()

    return True #not added so does not effect matching, therefore, maintain current matching status

def store_edges_to_update_in_traversal(traversal: EdgeTraversal, edges: set[PathEdge]):
    traversal.to_update.update(edges)

def update_all_in_bipartite_graph_no_type_check(traversal: EdgeTraversal, edges: set[PathEdge]):
    #update all edges in the bipartites without checking for traversal type
    for edge in edges:
        update_in_bipartite_graph_by_type_no_type_check(traversal.bipartiteTW, edge, [edge.TW])
        update_in_bipartite_graph_by_type_no_type_check(traversal.bipartitePT, edge, [edge.TW, edge.OW, edge.PT])
        update_in_bipartite_graph_by_type_no_type_check(traversal.bipartiteNPT, edge, [edge.TW, edge.OW, edge.NPT])

def update_in_bipartite_graph_by_type_no_type_check(BG: BipartiteGraph, edge: PathEdge, path_lists : list[PathList]):
    #Four possible states for an edge:
    #1. Just became DB and wasn't before (add)
    #2. Was DB and no longer is (remove)
    #3. Was DB and still is (update)
    #4. Wasn't DB and still isn't (NDB 0 > 1 or 1 < 0 but DB 0) #this last case, we ignore b/c we check for non zero edges in get traversal
    was_DB = edge in BG

    is_DB = True
    has_at_least_one_path = False

    #check if all paths are 
    for pl in path_lists:
        
        if len(pl) == 0: #dont check empty lists
            continue

        has_at_least_one_path = True

        if not pl.is_double_bookable():
            is_DB = False #Not DB
            break

    #if all path lists are empty, then this traversal type is impossible
    #Mark as DB so that it creates an impossible to assign edge in the BG
    #therefore making the traversal impossible
    if (not has_at_least_one_path):
        is_DB = True 

    if (was_DB and is_DB):
        BG.update_edge(edge, path_lists)
    elif (was_DB and not is_DB):
        BG.remove_edge(edge)
    elif (not was_DB and is_DB):
        BG.add_edge(edge, path_lists)

def check_bipartites_for_traversal_type(bipartite_TW: BipartiteGraph, bipartite_PT: BipartiteGraph, bipartite_NPT: BipartiteGraph):
    has_match_TW = bipartite_TW.check_for_valid_matching()
    has_match_PT = bipartite_PT.check_for_valid_matching()
    has_match_NPT = bipartite_NPT.check_for_valid_matching()

    new_traversal_type : TraversalType = get_traversal_type_from_possible_matchings(has_match_TW, has_match_PT, has_match_NPT)
    
    return new_traversal_type

def get_traversal_type_from_possible_matchings(has_match_TW: bool, has_match_PT: bool, has_match_NPT: bool):
    #The three bools tell us whether we can traverse that type without an impossible booking

    #If TW is not impossible, then any type can use it
    if (has_match_TW):
        return TraversalType.ANY

    #If PT and NPT are not impossible, then either OW type can use it
    if (has_match_PT and has_match_NPT):
        return TraversalType.OW

    #only PT can use it
    if (has_match_PT):
        return TraversalType.PIZZATIME

    if (has_match_NPT):
        return TraversalType.NOTPIZZATIME

    #No type can use it
    return TraversalType.INVALID

