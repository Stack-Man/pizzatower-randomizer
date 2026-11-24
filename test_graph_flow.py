from json_parse import parse_json_to_rooms_all, FILENAMES
from graph_create import rooms_to_graph, FlowGraphHandler
from graph_flow import flow
from graph_objects import DoorNode, EdgeTraversal, StartExitType, Edge, Node, PathEdge
import networkx as nx
from colors import WARNING, CAUTION, RESET, CONTINUE
from enums import DoorType, DoorDir
from settings import TraversalMode

from perf_counter import print_perf
from json_parse import FILENAMES

import cProfile
import pstats


def test_flow():

    fn = ["johngutter", "ancientcheese", "bloodsauce", "pizzascape",
          "fastfoodsaloon", "wasteyard", "funfarm", "oreganodesert", 
          "crustcove", "deepdish9", "gnomeforest", "golf",
           "ohshit", "freezer", "peppibotfactory", "thepigcity",
           "dontmakeasound", "pizzascare", "war", 
            "crumblingtowerofpizza", "trickytreat", "tutorial", "tutorial_noise"]

    #fn = ["johngutter"]
    
    print(f"{WARNING}PERFORMING FLOW WITH {CAUTION}{fn} {RESET}")
    all_rooms = parse_json_to_rooms_all(fn)

    graph = rooms_to_graph(all_rooms, traversal_mode = TraversalMode.MATCHING_PERFECT) 

    #graph = test_complete_graph()
    flow(graph)

    #print_steps(graph, print_traversals=False)

def count_all_traversals(FG: FlowGraphHandler):
    all = 0
    
    for N in FG.nodes():
        N: DoorNode

        for_N = 0

        

        for D, traversals in N.steps.items():
            if (for_N == 0):
                print(f"{WARNING}{N}:{RESET}")
            
            print(f"    {CONTINUE}{D}: {len(traversals)}{RESET}")
            
            for_N += len(traversals)

            for T in traversals:
               print(f"        {T}")

        if (for_N != 0):
            print(f"    TOTAL: {for_N} traversals")

        all += for_N

    print(f"Total: {all}")

def test_complete_graph():

    nodes = [

        DoorNode(DoorType.DOOR, DoorDir.NONE, StartExitType.START),
        DoorNode(DoorType.DOOR, DoorDir.NONE, StartExitType.EXIT),
        DoorNode(DoorType.BOX, DoorDir.UP, StartExitType.START),
        DoorNode(DoorType.BOX, DoorDir.UP, StartExitType.EXIT),
        DoorNode(DoorType.BOX, DoorDir.DOWN, StartExitType.START),
        DoorNode(DoorType.BOX, DoorDir.DOWN, StartExitType.EXIT)
    ]

    G = nx.DiGraph()

    G.add_nodes_from(nodes)

    for a in nodes:
        for b in nodes:
            if (a is not b):
                G.add_edge(a, b, object = Edge(a, b))

    return G


def print_steps(G: FlowGraphHandler, print_traversals: bool):

    print(f"STEPS of G:")

    for N in G.nodes():
        N : Node

        print(f"    {N}:")

        for destination, traversals in N.steps.items():
            print(f"        {N} > {destination}: {len(traversals)}")

    if (not print_traversals):
        return
    
    print(f"")

    for N in G.nodes():
            N : Node
    
            for destination, traversals in N.steps.items():
                print(f"{N} > {destination}: {len(traversals)}")

                for traversal in traversals:

                    print(f"    {traversal}")
    


profiler = cProfile.Profile()
profiler.enable()
test_flow()
profiler.disable()

# Sort results by cumulative time spent in each function
stats = pstats.Stats(profiler).sort_stats("cumtime")
stats.print_stats(15)  # Print top 10 slowest functions