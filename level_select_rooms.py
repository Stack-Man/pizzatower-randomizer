#Author: Stack Man
#Date: 11/11/2026

#select rooms and paths to fill the edges of the traversal

import networkx as nx
from graph_objects import EdgeTraversal
from level_objects import RoomSelection
from graph_from_rooms import FlowGraphHandler
from enums import TraversalType
from colors import WARNING, RESET

def select_rooms(FG: FlowGraphHandler, traversal: EdgeTraversal, traversal_type: TraversalType):
    print(f"{WARNING}select_rooms not implemented{RESET}")

    #on recieving a traversal, we have a guarnatee that there is not an impossible booking
    #or that we can avoid one utilizing the traversal's bipartite graphs

    #after selecting rooms, we may have depleted the NDB paths in an edge of the traversal and
    #must re-check traversals to confirm whether they have an impossible booking

    #we want to re-check all traversals containing the consumed edge 
    #and we want to do this before getting to select_rooms so we aren't 
    #given an already invalid traversal

    #we could, here, mark in FG edges that have been depleted of DB or NDB
    #in get_traversal() check all traversals containing those NDB depleted edges
    #for any of them, try to modify the bipartite graph to check for an impossible booking

    #also check for a completely depleted traversal and remove it



    return RoomSelection([])