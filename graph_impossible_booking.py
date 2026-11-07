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
import networkx as nx
from colors import ERROR, RESET, CAUTION

#bipartite_TW/PT/NPT: A bipartite graph constructed from the edge traversal up to this point
#traversal_type: priority traversal type accounting for a pathlist in edge being empty
#edge: An edge which might be DB
def add_to_bipartite_graph(bipartite_TW: nx.Graph, bipartite_PT: nx.Graph, bipartite_NPT: nx.Graph, traversal_type: TraversalType, edge: PathEdge):

    #check if type is already impossible or meets impossible booking reqs
    #TW = not OW, PT or NPT
    impossibleTW = (traversal_type != TraversalType.ANY or 
        add_to_bipartite_graph_by_type(bipartite_TW, edge, [edge.TW]))

    #PT = ANY PT or OW, but not NPT
    impossiblePT = (traversal_type == TraversalType.NOTPIZZATIME or 
                    add_to_bipartite_graph_by_type(bipartite_PT, edge, [edge.TW, edge.OW, edge.PT]))

    #NPT = AnNY NPT or OW but not PT
    impossibleNPT = (traversal_type == TraversalType.PIZZATIME or 
                     add_to_bipartite_graph_by_type(bipartite_NPT, edge, [edge.TW, edge.OW, edge.NPT]))

    new_traversal_type = get_traversal_type_from_impossible_bookings(impossibleTW, impossiblePT, impossibleNPT)

    print(f"add edge {edge} to traversal")
    print(f"    {traversal_type} to {new_traversal_type} - Impossible TW: {impossibleTW}; PT: {impossiblePT}; NPT: {impossibleNPT}") 


    return new_traversal_type

#path_lists: tuple pairs of NDB and DB rooms, all pairs must be DB only to add
def add_to_bipartite_graph_by_type(BG: nx.Graph, edge: PathEdge, path_lists: list[PathList]):

    #1. Confirm edge is DB (all PathLists contain only DB)
    for pl in path_lists:
        if not pl.is_double_bookable():
            return False #not valid edge to check

    #2. Create node E with edge
    E = PathEdgeNode(edge)

    #3. Create nodes Rs from DB rooms in PathLists.DBs (no object for room is needed so duplicating node is okay)
    Rs = room_nodes_from_path_lists(path_lists)

    #4. add E and Rs to BG
    #5. add edge to BG for each [E, R] 
    BG.add_node(E, bipartite=0)

    for R in Rs:
        BG.add_node(R, bipartite=1)
        BG.add_edge(E, R)
    
    #6. for each connected component, check if R < E and if so, return False

    for connected_component in nx.connected_components(BG):
        if more_nodes_in_group_zero(BG, connected_component):
            print(f"{CAUTION}{RESET}")
            return False #Impossible Booking discovered

    return True

def more_nodes_in_group_zero(BG, group):

    zero = 0
    one = 0

    for n in group:
        if (BG.nodes[n]["bipartite"] == 0):
            zero += 1
        else:
            one += 1

    return zero > one

def room_nodes_from_path_lists(path_lists: list[PathList]):
    names = []

    #make one room node for every unique room name on each path
    for path_list in path_lists:
        for p in path_list:

            if (p.room_name == ""):
                print(f"{ERROR}{RESET}")
            elif (p.room_name not in names):
                names.append(p.room_name)

    rooms = []

    for name in names:
        rooms.append(RoomNode(name))

    return rooms

def get_traversal_type_from_impossible_bookings(impossibleTW: bool, impossiblePT: bool, impossibleNPT: bool):
    #The three bools tell us whether we can traverse that type without an impossible booking

    #If TW is not impossible, then any type can use it
    if (not impossibleTW):
        return TraversalType.ANY

    #If PT and NPT are not impossible, then either OW type can use it
    if (not impossiblePT and not impossibleNPT):
        return TraversalType.OW

    #only PT can use it
    if (not impossiblePT):
        return TraversalType.PIZZATIME

    if (not impossibleNPT):
        return TraversalType.NOTPIZZATIME

    #No type can use it
    return TraversalType.INVALID

class PathEdgeNode():
    def __init__(self, path_edge: PathEdge):
        self.path_edge = path_edge

    def __eq__(self, other):
        return self == other

    def __hash__(self):
        return hash(self.path_edge)

class RoomNode():
    def __init__(self, room_name: str):
        self.room_name = room_name

    def __eq__(self, other):
        return self == other

    def __hash__(self):
        return hash(self.room_name)
    