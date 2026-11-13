#Author: Stack Man
#Date: 11/12/2026

#clean up traversals in FG based on FG.depleted_edges
#update the traversal type based on the OG traversal type and the new state of the edge

from graph_from_rooms import FlowGraphHandler
from graph_objects import DoorNode, CombinedDoorNode, EdgeTraversal, PathEdge
from enums import TraversalType
from graph_impossible_booking import add_to_bipartite_graph
 
LOGGING = True

def log(msg: str):
    if (LOGGING):
        print(msg)

def clean_depleted_traverals(FG: FlowGraphHandler):

    for edge in FG.depleted_edges:
        for traversal, node, destination in all_traversals(FG):
            if (edge in traversal):
                update_traversal_type(node, destination, traversal, edge)

    FG.depleted_edges.clear()

    return FG

def all_traversals(FG: FlowGraphHandler):
    for N in FG.nodes():
        N: DoorNode|CombinedDoorNode
        for D, traversals in N.steps.items():
            for t in traversals:
                yield t, N, D

def update_traversal_type(node: DoorNode | CombinedDoorNode, destination: DoorNode, traversal: EdgeTraversal, edge: PathEdge):
    new_traversal_type = add_to_bipartite_graph(traversal.bipartiteTW, traversal.bipartitePT, traversal.bipartiteNPT, traversal.traversal_type, edge)
    old_traversal_type = traversal.traversal_type
    traversal.traversal_type = new_traversal_type

    log(f"traversal type from {old_traversal_type} to {new_traversal_type}")

    if (new_traversal_type == TraversalType.INVALID):
        node.steps[destination].remove(traversal)
        log(f"traversal to {destination} removed from {node}. now has {len(node.steps[destination])} traversals")