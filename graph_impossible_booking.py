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

from graph_objects import PathEdge, PathList
from enums import TraversalType
import networkx as nx
from colors import ERROR, RESET, CAUTION 

import logging as log

#These first two functions are used during traversal construction to check traversal type
#as we create the traversal, allowing us to terminate invalid traversals
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

    #no need to make an OW bipartite graph as there is never a timeless OW path needed
    #(CTOP is PT and WAR is NPT) 
    #OW is simply a generic "both PT and NPT can work"

    new_traversal_type : TraversalType = get_traversal_type_from_impossible_bookings(impossibleTW, impossiblePT, impossibleNPT)

    return new_traversal_type

#path_lists: tuple pairs of NDB and DB rooms, all pairs must be DB only to add
#return TRUE: impossible, FALSE: not impossible
def add_to_bipartite_graph_by_type(BG: nx.Graph, edge: PathEdge, path_lists: list[PathList]):

    #Confirm edge is DB (all PathLists contain only DB)
    has_at_least_one_path = False

    for pl in path_lists:
        if len(pl) == 0: #dont check empty lists
            continue

        has_at_least_one_path = True

        if not pl.is_double_bookable():
            return False #not valid edge to check, so return as NOT impossible

    #if all path lists are empty, then this traversal type is impossible
    if (not has_at_least_one_path):
        return True

    #Add Edge as an E node
    #and DB rooms that can satisfy that edge as R nodes'
    E = PathEdgeNode(edge)

    if (E not in BG):
        add_edge_to_BG(BG, edge, path_lists)

    #for each connected component, check if R < E and if so, return IMPOSSIBLE
    return check_for_impossible_booking(BG)

#The following is used during level_clean_replenish to update traversals
#whose DB edges have changed status
def update_in_bipartite_graph(bipartite_TW: nx.Graph, bipartite_PT: nx.Graph, bipartite_NPT: nx.Graph, edge: PathEdge):
    impossibleTW = update_in_bipartite_graph_by_type(bipartite_TW, edge, [edge.TW])
    impossiblePT = update_in_bipartite_graph_by_type(bipartite_PT, edge, [edge.TW, edge.OW, edge.PT])
    impossibleNPT = update_in_bipartite_graph_by_type(bipartite_NPT, edge, [edge.TW, edge.OW, edge.NPT])

    new_traversal_type : TraversalType = get_traversal_type_from_impossible_bookings(impossibleTW, impossiblePT, impossibleNPT)

    return new_traversal_type

def update_all_in_bipartite_graph_no_type_check(bipartite_TW: nx.Graph, bipartite_PT: nx.Graph, bipartite_NPT: nx.Graph, edges: set[PathEdge]):
    #update all edges in the bipartites without checking for traversal type
    for edge in edges:
        update_in_bipartite_graph_by_type_no_type_check(bipartite_TW, edge, [edge.TW])
        update_in_bipartite_graph_by_type_no_type_check(bipartite_PT, edge, [edge.TW, edge.OW, edge.PT])
        update_in_bipartite_graph_by_type_no_type_check(bipartite_NPT, edge, [edge.TW, edge.OW, edge.NPT])

def update_in_bipartite_graph_by_type_no_type_check(BG: nx.Graph, edge: PathEdge, path_lists : list[PathList]):
    #Four possible states for an edge:
    #1. Just became DB and wasn't before (add)
    #2. Was DB and no longer is (remove)
    #3. Was DB and still is (update)
    #4. Wasn't DB and still isn't (NDB 0 > 1 or 1 < 0 but DB 0) #this last case, we ignore b/c we check for non zero edges in get traversal

    E = PathEdgeNode(edge)
    was_DB = E in BG

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
    if (not has_at_least_one_path):
        is_DB = False #Mark as NOT DB so it is removed

    if (was_DB and is_DB):
        update_edge_in_BG(BG, edge, path_lists)
    elif (was_DB and not is_DB):
        remove_edge_from_BG(BG, edge)
    elif (not was_DB and is_DB):
        add_edge_to_BG(BG, edge, path_lists)

def update_in_bipartite_graph_by_type(BG: nx.Graph, edge: PathEdge, path_lists : list[PathList]):
    update_in_bipartite_graph_by_type_no_type_check(BG, edge, path_lists)
    return check_for_impossible_booking(BG)

def check_bipartites_for_traversal_type(bipartite_TW: nx.Graph, bipartite_PT: nx.Graph, bipartite_NPT: nx.Graph):
    impossibleTW = check_for_impossible_booking(bipartite_TW)
    impossiblePT = check_for_impossible_booking(bipartite_PT)
    impossibleNPT = check_for_impossible_booking(bipartite_NPT)

    new_traversal_type : TraversalType = get_traversal_type_from_impossible_bookings(impossibleTW, impossiblePT, impossibleNPT)
    
    return new_traversal_type


#modify room to edge connections in BG for edge E
def update_edge_in_BG(BG: nx.Graph, edge: PathEdge, path_lists : list[PathList]):

    E = PathEdgeNode(edge)
    Rs = room_nodes_from_path_lists(path_lists)

    #add all rooms and edges to them
    #duplicates don't re-add
    for R in Rs:
        BG.add_node(R, bipartite=1)
        BG.add_edge(E, R)

    #remove edges to rooms connected to E but not in Rs
    #leave the node in case its attached to another E
    #isolated Rs are OK
    #use LIST to avoid "modify dictionary during iteration" error
    for R in list(BG.neighbors(E)):
        if R not in Rs:
            BG.remove_edge(E, R)

def remove_edge_from_BG(BG: nx.Graph, edge: PathEdge):

    E = PathEdgeNode(edge)

    #automatically disconnects all edges to E
    #isolated Rs are OK 
    BG.remove_node(E)

def add_edge_to_BG(BG: nx.Graph, edge: PathEdge, path_lists : list[PathList]):

    E = PathEdgeNode(edge)
    Rs = room_nodes_from_path_lists(path_lists)

    BG.add_node(E, bipartite=0)

    for R in Rs:
        BG.add_node(R, bipartite=1)
        BG.add_edge(E, R)

def check_for_impossible_booking(BG: nx.Graph):

    #6. for each connected component, check if R < E and if so, return IMPOSSIBLE
    for connected_component in nx.connected_components(BG):
        if more_nodes_in_group_zero(BG, connected_component):
            return True #Impossible Booking discovered

    return False #not impossible booking 

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

        self._hash = hash(self.path_edge)

    def __eq__(self, other):
        if (type(other) != PathEdgeNode):
            return False

        return self.path_edge == other.path_edge

    def __hash__(self):
        return self._hash

class RoomNode():
    def __init__(self, room_name: str):
        self.room_name = room_name

    def __eq__(self, other):
        if (type(other) != RoomNode):
            return False

        return self.room_name == other.room_name

    def __hash__(self):
        return hash(self.room_name)
    