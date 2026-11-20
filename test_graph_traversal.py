#Author: Stack Man
#Date: 11/19/2026

from graph_create import rooms_to_graph
from json_parse import parse_json_to_rooms_all
from graph_collapse import collapse_all_nodes_and_edges
from graph_flow import flow
from graph_objects import PathEdge, TransitionEdge, DoorNode, CombinedDoorNode, EdgeTraversal

FN = ["johngutter"]

import log_config
import logging as log

def test_get_traversals():
    rooms = parse_json_to_rooms_all(FN)
    FG = rooms_to_graph(rooms)
    FG = collapse_all_nodes_and_edges(FG)
    FG = flow(FG)

    for N in FG.nodes():
        N : DoorNode | CombinedDoorNode

        for D, Ts in N.steps.items():
            log.debug("D: %s", D)

            for T in Ts:
                print_traversal(T)


def print_traversal(traversal: EdgeTraversal):

    log.debug("     traversal: %s", traversal)

    for edge in traversal:
        if (type(edge) == PathEdge):
            log.debug("         edge: %s", edge)

            log.debug("             paths: %s", str(edge.TW))
            log.debug("             paths: %s", str(edge.OW))
            log.debug("             paths: %s", str(edge.NPT))
            log.debug("             paths: %s", str(edge.PT))

test_get_traversals()
            


    

