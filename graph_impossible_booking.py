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



from graph_objects import PathEdge, EdgeTraversal, PathList
from objects import Path
from enums import TraversalType

#traversal: the current traversal we are checking an impossible booking on
#edge: An edge which might be DB
def add_to_bipartite_graph(traversal: EdgeTraversal, edge: PathEdge):

    traversal_type = traversal.traversal_type

    #check if type is already impossible or meets impossible booking reqs
    #TW = not OW, PT or NPT
    impossibleTW = (traversal_type != TraversalType.ANY or 
        add_to_bipartite_graph_by_type(traversal.bipartiteTW, edge, [edge.TW]))

    #PT = ANY PT or OW, but not NPT
    impossiblePT = (traversal_type == TraversalType.NOTPIZZATIME or 
                    add_to_bipartite_graph_by_type(traversal.bipartitePT, edge, [edge.TW, edge.OW, edge.PT]))

    #NPT = AnNY NPT or OW but not PT
    impossibleNPT = (traversal_type == TraversalType.PIZZATIME or 
                     add_to_bipartite_graph_by_type(traversal.bipartiteNPT, edge, [edge.TW, edge.OW, edge.NPT]))

    #TODO: modify traversal type based on results of bipartite graph
    return impossibleTW, impossiblePT, impossibleNPT

#path_lists: tuple pairs of NDB and DB rooms, all pairs must be DB only to add
def add_to_bipartite_graph_by_type(BG, edge: PathEdge, path_lists: list[PathList]):

    #TODO:
    #1. Confirm edge is DB (all PathLists contain only DB)
    #2. Create node E with edge
    #3. Create nodes Rs from DB rooms in PathLists.DBs (no object for room is needed so duplicating node is okay)
    #4. add E and Rs to BG
    #5. add edge to BG for each [E, R] 
    #6. for each connected component, check if R < E and if so, return False

    return True