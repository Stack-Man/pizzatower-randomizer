#Author: Stack Man
#Date: 11/2/2026

#The "flow" algorithm in this file populates every START node in the graph with
#a list of EXIT destinations that it can reach and the edge traversal for every
#unique list of edges that can be followed to get there. 

#Exclude traversals that contain an edge subset that is the same as the edge set of a shorter edge traversal.
#Mark traversals that can only be completed via paths in an NPT, PT, or OWANY path category.
#Exclude traversals that can only be completed utilizing paths in both an NPT and PT path category.
#Give every traversal a rarity score based on the frequency and rarity of the path types used to complete it.
#Exclude traversals taht can only be completed by double-booking a set of rooms

#Pseudo Code:
#For N in Nodes:
#   N.Steps_Round_0[N] = 0, {}
#For R in Rounds: //until no changes or R = N
#   For N in Nodes: //Run concurrently
#       For P in N.Parents:
#           For [Destination] = steps, {path}  in N.Steps_Round_R-1
#               if {path} does not contain P 
#                   if {path} does not contain a subset in P.Steps_Round_X //Must check all sets
#                       P.Steps_Round_R[Destination] = steps + 1, {path + N}

import networkx as nx
from graph_objects import EdgeTraversal, DoorNode, CombinedDoorNode, StartExitType, PathEdge, TransitionEdge
from graph_impossible_booking import add_to_bipartite_graph
import threading

from enums import DoorType, DoorDir, TraversalType

from colors import WARNING, RESET, CAUTION

import time

LOGGING = True

#can an additional optimization be made considering steps with START vs EXIT nodes?
#a START node doesnt need to know how to reach other START nodes
#an EXIT node will never have its steps list read
#though they may be necessary for the flow process even if the end result is unneeded.
def flow(G):
    log(f"Flow of G with {len(G.nodes())} nodes and {len(G.edges())} Edges begin")

    #initialize nodes with traversal to self
    for N in G.nodes():
        N.last_steps[N] = [EdgeTraversal([], rarity=0)]

    R = 1
    total_time = 0
    G.changed_last_round = True #store value in shared G so any thread can modify it

    while (G.changed_last_round and R < len(G.nodes())):

        G.changed_last_round = False

        threads = []

        start_time = time.perf_counter()



        #pass all valid edge traversal from N to its parents P
        for N in G.nodes():
            t = threading.Thread(target = pass_steps_to_parents, args=(G, N))
            threads.append(t)
            t.start()      

        for t in threads:
            t.join()

        threads = []

        #At the end of every round, save next to steps, last = next and clear next
        #ensures all nodes complete before modifying N.steps and tracks this round's steps
        
        for N in G.nodes():
            t = threading.Thread(target = store_steps, args=(N,))
            threads.append(t)
            t.start()
            
               
        for t in threads:
            t.join() 

        end_time = time.perf_counter()

        process_time = end_time - start_time
        total_time += process_time

        log(f"Round {R}: ({process_time})")

        R = R + 1

    log(f"Total Time: ({total_time})")

    #clean up node steps, remove traversals stored in START nodes
    #generations only occur from an EXIT to a START
    for N in G.nodes():

        if (N.se_type == StartExitType.START):
            N.steps = {}
        else:
            #cleanup remove destinations that are EXIT from steps
            
            to_remove = []

            for destination, traversals in N.steps.items():
                if (destination.se_type == StartExitType.EXIT):
                    to_remove.append(destination)

            for d in to_remove:
                N.steps.pop(d, None)

    return G

def contains_repeat_subset(subset_traversals: dict[DoorNode | CombinedDoorNode, list[EdgeTraversal]], superset_traversal : EdgeTraversal):

    for _, traversals in subset_traversals.items():
        for subset in traversals:
            if superset_traversal.contains_subset(subset):
                return True

    return False

def pass_steps_to_parents(G, N: DoorNode | CombinedDoorNode):

    start_time = time.perf_counter()

    for P in G.predecessors(N):
        P : DoorNode

        #pass all valid traversals in N to parent P
        for destination, traversals in N.last_steps.items():

            size = len(P.next_steps)

            if (destination not in P.next_steps):
                P.next_steps[destination] = []

            for traversal in traversals:
                if (destination == P or traversal.contains(P)): #skip traversals that contain self
                    continue

                new_edge : PathEdge | TransitionEdge = (G.get_edge_data(P, N)["object"])
                new_traversal_type = TraversalType.ANY #default for TransitionEdge

                #exclusions only need to be performed on PathEdges, not TrasnitionEdges
                if (type(new_edge) == PathEdge):
                    #Get traversal type of this edge
                    #based on available path types    
                    edge_traversal_type = get_edge_traversal_type(new_edge)

                    #no paths in the edge
                    if (edge_traversal_type == TraversalType.INVALID):
                        continue

                    old_traversal_type = traversal.traversal_type

                    #skip traversals where NPT only crosses into PT only
                    if (   (edge_traversal_type == TraversalType.PIZZATIME and old_traversal_type == TraversalType.NOTPIZZATIME)
                        or (edge_traversal_type == TraversalType.NOTPIZZATIME and old_traversal_type == TraversalType.PIZZATIME)):
                        continue

                    #Traversal type priority: TW < OW < NPT/PT
                    priority_traversal_type = get_priority_traversal_type(edge_traversal_type, old_traversal_type)

                    #exclude traversals that require double booking rooms

                    #Create shallow copies of the bipartite graph for the new edge traversal
                    #to avoid modifying the graphs of the original traversal
                    #(the graphs will be re-used during path selection)
                    new_bipartite_TW = traversal.bipartiteTW.copy()
                    new_bipartite_PT = traversal.bipartitePT.copy()
                    new_bipartite_NPT = traversal.bipartiteTW.copy()

                    #create bipartite graphs to determine connected components where R < E
                    new_traversal_type = add_to_bipartite_graph(new_bipartite_TW, new_bipartite_PT, new_bipartite_NPT, priority_traversal_type, new_edge)

                    #no valid path exists
                    if (new_traversal_type == TraversalType.INVALID):
                        continue

                #get the edge set and prepend the current edge to the front
                #use a copy() to avoid mutating the same list later
                new_edge_list = traversal.edges.copy()
                new_edge_list.insert(0, new_edge)

                #create new traversal including this edge
                #TODO: determine rarity
                new_traversal = EdgeTraversal(new_edge_list, rarity=0, traversal_type=new_traversal_type)

                P.next_steps[destination].append(new_traversal)

                G.changed_last_round = True

    end_time = time.perf_counter()

def get_edge_traversal_type(edge : PathEdge | TransitionEdge):

    traversal_type = TraversalType.ANY

    if (type(edge) is PathEdge):
        has_npt = len(edge.NPT) > 0
        has_pt  = len(edge.PT) > 0
        has_owany = len(edge.OW) > 0
        has_twany = len(edge.TW) > 0

        #has_twany = valid for any
        #not = NPT PT or OW

        if (not has_twany):

            #has OW or has both PT and NPT
            if (has_owany or (has_pt and has_npt)):
                traversal_type = TraversalType.OW

            #no OW and exclusive to one or the other
            elif (has_pt and not has_npt):
                traversal_type = TraversalType.PIZZATIME
            elif (has_npt and not has_pt):
                traversal_type = TraversalType.NOTPIZZATIME
            elif (not has_pt and not has_owany and not has_npt):
                traversal_type = TraversalType.INVALID #no available paths

    return traversal_type

def get_priority_traversal_type(edge_type: TraversalType, old_type: TraversalType):
    #Traversal type priority: TW < OW < NPT/PT

    if (old_type == TraversalType.PIZZATIME or old_type == TraversalType.NOTPIZZATIME):
        return old_type

    if (edge_type == TraversalType.PIZZATIME or edge_type == TraversalType.NOTPIZZATIME):
        return edge_type

    if (old_type == TraversalType.OW or edge_type == TraversalType.OW):
        return TraversalType.OW

    return TraversalType.ANY


def store_steps(N: DoorNode):

    #don't store traversals with 0 traversals
    #must do this outside the pass step to avoid multiple access from different threads
    for destination, traversals in N.next_steps.items():
        traversal_count = len(traversals)

        if (destination not in N.steps and traversal_count > 0):
            N.steps[destination] = []

        if (traversal_count > 0):
            N.steps[destination].extend(traversals)

    N.last_steps = N.next_steps.copy()
    N.next_steps = {}

def log(msg: str):
    if (LOGGING):
        print(msg, flush=True)
