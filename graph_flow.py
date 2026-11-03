#Author: Stack Man
#Date: 11/2/2026

#The "flow" algorithm in this file populates every START node in the graph with
#a list of EXIT destinations that it can reach and the edge traversal for every
#unique list of edges that can be followed to get there. 

#Exclude traversals that contain an edge subset that is the same as the edge set of a shorter edge traversal.
#Mark traversals that can only be completed via paths in an NPT, PT, or OWANY path category.
#Exclude traversals that can only be completed utilizing paths in both an NPT and PT path category.
#Give every traversal a rarity score based on the frequency and rarity of the path types used to complete it.

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
from graph_objects import EdgeTraversal, DoorNode
import threading


#can an additional optimization be made considering steps with START vs EXIT nodes?
#a START node doesnt need to know how to reach other START nodes
#an EXIT node will never have its steps list read
#though they may be necessary for the flow process even if the end result is unneeded.
def flow(G):

    #initialize nodes with traversal to self
    for N in G.nodes():
        N.last_steps[N] = [EdgeTraversal([], 0, False, False, False)]

    R = 1
    G.changed_last_round = True #store value in shared G so any thread can modify it

    while (G.changed_last_round and R < len(G.nodes())):

        G.changed_last_round = False

        threads = []

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
            t = threading.Thread(target = store_steps, args=(N))
            threads.append(t)
            t.start()
               
        for t in threads:
            t.join() 
           
    return G

def contains_repeat_subset(subset_traversals: dict[DoorNode, list[EdgeTraversal]], superset_traversal : EdgeTraversal):

    for _, traversals in subset_traversals.items():
        for subset in traversals:
            if superset_traversal.contains_subset(subset):
                return True

    return False

def pass_steps_to_parents(G, N: DoorNode):

    for P in G.predecessors(N):
        P : DoorNode

        #pass all valid traversals in N to parent P
        for destination, traversals in N.last_steps.items():

            if (destination not in P.next_steps):
                P.next_steps[destination] = []

            for traversal in traversals:
                if (destination == P or traversal.contains(P)): #skip traversals that contain self
                    continue

                if (contains_repeat_subset(P.steps, traversal)): #skip traversals that contain a subset in P.steps
                    continue

                #TODO: exclude traversals that require both NPT and PT exclusive paths
                #aka, exclude traversals marked as NPT or PT if this edge is exclusive to the opposite
                
                #get the edge set and prepend the current edge to the front
                new_edge_list = traversal.edges
                new_edge_list.insert(0, (G.get_edge_data(P, N)["object"]))

                #create new traversal including this edge
                #TODO: determine rarity and path types
                new_traversal = EdgeTraversal(new_edge_list, 0, False, False, False)

                P.next_steps[destination].append(new_traversal)
                P.steps[destination].append(new_traversal)

                G.changed_last_round = True

def store_steps(N: DoorNode):
    for destination, traversals in N.next_steps.items():
        if (destination not in N.steps):
            N.steps[destination] = traversals
        else:
            N.steps[destination].extend(traversals)

        N.last_steps = N.next_steps
        N.next_steps = {}