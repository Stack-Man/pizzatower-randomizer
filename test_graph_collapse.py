#Author: Stack Man
#Date: 11/4/2026

from json_parse import parse_json_to_rooms_all, FILENAMES
from graph_create import rooms_to_graph
from graph_collapse import collapse_all_nodes_and_edges, FlowGraphHandler
from settings import TraversalMode
from graph_flow import flow

def test_collapse():

    all_rooms = parse_json_to_rooms_all(FILENAMES)
    graph = rooms_to_graph(all_rooms, traversal_mode=TraversalMode.ARBITRARY_NO_RESTRICTIONS)
    collapsed_graph = collapse_all_nodes_and_edges(graph)

    print_graph(collapsed_graph)

    #flow(graph)
    #flow(collapsed_graph)

def print_graph(FG : FlowGraphHandler):

    print("Nodes:")

    for N in FG.nodes():
        print(f"    {N}")

    print("Edges:")

    for U, V in FG.edges():
        print(f"    {U} to {V}")

test_collapse()