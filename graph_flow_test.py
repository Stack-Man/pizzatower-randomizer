from json_parse import parse_json_to_rooms_all, FILENAMES
from graph_from_rooms import rooms_to_graph
from graph_flow import flow
from graph_objects import DoorNode, EdgeTraversal, StartExitType, Edge
import networkx as nx
from colors import WARNING, CAUTION, RESET
from enums import DoorType, DoorDir

def test_flow():

    fn = ["johngutter", "ancientcheese", "bloodsauce", "pizzascape",
          "fastfoodsaloon", "wasteyard", "funfarm", "oreganodesert", 
          "crustcove", "deepdish9", "gnomeforest", "golf",
           "ohshit", "freezer", "peppibotfactory", "thepigcity",
           "dontmakeasound", "pizzascare", "war", 
            "crumblingtowerofpizza", "trickytreat", "tutorial", "tutorial_noise"]
    
    #print(f"{WARNING}PERFORMING FLOW WITH {CAUTION}{fn} {RESET}")
    #all_rooms = parse_json_to_rooms_all(fn)
    #graph = rooms_to_graph(all_rooms)
    
    #TODO: processing does not find any repeat subsets and the processing time
    #grows factorially as a consequence.

    #Likely, it is because the destinations are unique, and the repeat subset theory does not actually work anymore because
    #1 it doesnt actually cross check between different destinations for subsets
    #2 i do actually need every unqiue combination that visits a different destination even if it contains repeat subsets from the source
    #maybe i can think about it backwards or something?

    #TODO TODO TODO TODO:
    #i need to exclude larger paths that include ANY of the edges of smaller ones?
    #because no matter what that smmaller path si included? NO thats not it
    #because then if the repeated edge is common then i dont care if both paths use it, the longer one might still have a lower rarity score

    graph = test_complete_graph()
    flow(graph)

    print_steps(graph)

def test_complete_graph():

    nodes = [
        DoorNode(DoorType.A, DoorDir.X, StartExitType.X),
        DoorNode(DoorType.B, DoorDir.X, StartExitType.X),
        DoorNode(DoorType.C, DoorDir.X, StartExitType.X),
        DoorNode(DoorType.D, DoorDir.X, StartExitType.X),
        DoorNode(DoorType.E, DoorDir.X, StartExitType.X)
        #DoorNode(DoorType.DOOR, DoorDir.NONE, StartExitType.START),
        #DoorNode(DoorType.DOOR, DoorDir.NONE, StartExitType.EXIT),
        #DoorNode(DoorType.BOX, DoorDir.UP, StartExitType.START),
        #DoorNode(DoorType.BOX, DoorDir.UP, StartExitType.EXIT),
        #DoorNode(DoorType.BOX, DoorDir.DOWN, StartExitType.START),
        #DoorNode(DoorType.BOX, DoorDir.DOWN, StartExitType.EXIT)
    ]

    G = nx.DiGraph()

    G.add_nodes_from(nodes)

    for a in nodes:
        for b in nodes:
            if (a is not b):
                G.add_edge(a, b, object = Edge(a, b))

    return G

#TODO: our repeated edge subset detection removes valid traversals between two unqiue destinations when the subset appears as a traversal to a different
#destination. For instance, Door > Hall Left > Hall Right is exclusive with Door > Hall Left > Hall Right > Box Up, even if there is no other way to 
#reach Box Up (actually does it? im not sure, there was a different bug)

#TODO: calculate rarity score and only keep the least rare path to a destination? No, because if one path can be extended to be less rare for another source
#then i need to pass it, even if its not the least rare for that path
#maybe tehre is an optimization i could make however

#Current running time is 13s with only 4/5 floors included
#this time will decrease with each flow as edges are lost, but it doesn't bode well for the full level generation

#for all 5 floors, it increases to quite a fucking lot, 148s, thats way too long

#TODO: repeat subset check takes 1563 time (divided by threads) if wea ssume an average it took 80s to process
#but found ZERO repeat subsets, is this unncessary? try a complete directed grapha nd see if it finds any
#It isn't, its possible the check is faulty, taking time finding no repeat subsets but 
#still processinga ll of those traversals its supposed to find

def print_steps(G: nx.DiGraph):

    print(f"")

    for N in G.nodes():
        N : DoorNode

        for destination, traversals in N.steps.items():
            print(f"{N} > {destination}: {len(traversals)}")

    print(f"")

    for N in G.nodes():
            N : DoorNode
    
            for destination, traversals in N.steps.items():
                print(f"{N} > {destination}: {len(traversals)}")

                for traversal in traversals:

                    print(f"    {traversal}")
    

test_flow()