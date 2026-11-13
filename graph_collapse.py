#Author: Stack Man
#Date: 11/4/2026

#Combine nodes and edges in the flow graph to reduce node and edge count and improve flow performance.
#START nodes with the same set of parents should combine.
#EXIT nodes with the same set of children should combine.
#PathEdges should continue to connect their original node, or the new combined node if it was replaced.
#Edges should combine if their start and end nodes are the same after combination

#Steps:
#1. For every pair of start nodes, combine those that have the same list of parents
#1b. repeat until no more new nodes are created

#2. For every pair of exit nodes, combine those that have the same list of children
#2b. repeat until no more new nodes are created

#3. For every edge in the graph, replace its original start and end node with the
#new combined nodes that contain their original node, if it was created

#4. For every edge taht shares the same start and end nodes, keep one and combine their lists of paths

#Pseduocode:
# For a, b in G.nodes
#   if a != b and a & b not in modified_nodes
#       if a & b == START
#           if a.parents == b.parents
#               ab = a + b
#               new_nodes += ab
#       else if a & b == EXIT
#           if a.children ==b.children
#               ab = a + b
#               new_nodes += ab
#
# new_G = new_nodes + unchanged_nodes
# if new_G.nodes < G.nodes
#   collapse(new_G)
#
# for edge in G
#   edge.a = G.node.contains_a
#   edge.b = G.node.contains_b
#
# for U, V in G.edges
#   if U.start == V.start and U.end == V.end
#       UV = U + V

import networkx as nx
from graph_objects import DoorNode, CombinedDoorNode, PathEdge, TransitionEdge
from graph_from_rooms import graph_from_nodes_and_edges, FlowGraphHandler
from enums import StartExitType
from colors import ERROR, RESET

from pairs import pairs

def collapse_all_nodes_and_edges(G: FlowGraphHandler):
    old_nodes = list(G.nodes())
    old_count = len(old_nodes)
    
    #Store list of parents/children in each node for easy access 
    #without reconstructing the graph each loop
    for n in old_nodes:
        n: DoorNode | CombinedDoorNode

        if (n.se_type == StartExitType.START):
            for p in G.predecessors(n):
                n.parents.append(p)

        elif (n.se_type == StartExitType.EXIT):
            for c in G.successors(n):
                n.children.append(c)

    new_nodes = collapse_nodes_repeat(old_nodes)

    old_edges = get_edges_from_graph(G.G)
    old_edge_count = len(old_edges)
    updated_edges = update_edge_nodes(old_edges, new_nodes)
    new_edges = collapse_edges_repeat(updated_edges)

    new_G = graph_from_nodes_and_edges(new_nodes, new_edges)

    print(f"G {old_count} nodes and {old_edge_count} edges collapse to {len(new_nodes)} nodes and {len(new_edges)} edges")

    G.G = new_G

    return G

def collapse_nodes_repeat(old_nodes: list[DoorNode|CombinedDoorNode]):
    new_nodes = old_nodes

    while (True):
        last_nodes = new_nodes
        new_nodes = collapse_nodes(new_nodes)

        print(f"collapsed {len(last_nodes)} nodes to {len(new_nodes)}", flush = True)

        #repeat until new_nodes stops shrinking
        if (len(new_nodes) >= len(last_nodes)):
            break

    return new_nodes

def collapse_nodes(nodes: list[DoorNode|CombinedDoorNode]):
    new_nodes = []

    for n in nodes:
        n.combined = False

    #combine every pair of nodes with the same parents/children that hasnt already been combined
    for a, b in pairs(nodes):

        if not a.combined and not b.combined:
            #same se_type and either start with same parents or exit with same children

            #must be same type
            if (a.se_type != b.se_type):
                #print(f"    {a} and {b} are not the same se_type {a.se_type} vs {b.se_type}")
                continue

            #lists of parents or children are the same
            if ((a.se_type == StartExitType.START and same_lists(a.parents, b.parents)) or
                (a.se_type == StartExitType.EXIT and same_lists(a.children, b.children))):
                #print(f"    {a} and {b} are collapsed")
                new_node = create_combined_node(a, b)
                new_nodes.append(new_node)
                a.combined = True
                b.combined = True
            #else:
                #print(f"    {a} and {b} do not have the same lists of parents {a.parents} vs {b.parents}")
                #print(f"    OR {a} and {b} do not have the same lists of children {a.children} vs {b.children}")

                
    #add every node that wasn't combined
    #nodes that weren't combined this round may be combined
    #next round with a combined node,
    #so we should re-check every round
    for n in nodes:
        if not n.combined:
            new_nodes.append(n)

    return new_nodes

def create_combined_node(a: DoorNode | CombinedDoorNode, b: DoorNode | CombinedDoorNode):

    all_nodes = []

    if (type(a) == CombinedDoorNode):
        all_nodes.extend(a.nodes)
    else:
        all_nodes.append(a)

    if (type(b) == CombinedDoorNode):
        all_nodes.extend(b.nodes)
    else:
        all_nodes.append(b)

    new_node = CombinedDoorNode(all_nodes, a.se_type)

    #only the parents or the children are shared
    if (new_node.se_type == StartExitType.START):
        new_node.parents = a.parents
    elif (new_node.se_type == StartExitType.EXIT):
        new_node.children = a.children

    return new_node

def same_lists(list_a: list[DoorNode|CombinedDoorNode], list_b: list[DoorNode|CombinedDoorNode]):

    #all a is in b
    for a in list_a:
        if a not in list_b:
            return False

    #all a is in b but b has more than a
    if len(list_a) < len(list_b):
        return False

    return True



def get_edges_from_graph(G: nx.DiGraph):
    edges = []

    for _, _, edge in G.edges.data("object"):
        edges.append(edge)

    return edges

def update_edge_nodes(old_edges: list[PathEdge|TransitionEdge], new_nodes: list[DoorNode | CombinedDoorNode]):

    updated_edges = []

    for edge in old_edges:

        new_start = node_containing_node(edge.start_node, new_nodes)
        new_end = node_containing_node(edge.end_node, new_nodes)

        edge.start_node = new_start
        edge.end_node = new_end

        updated_edges.append(edge)

    return updated_edges

def node_containing_node(node: DoorNode | CombinedDoorNode, nodes: list[DoorNode | CombinedDoorNode]):

    for candidate in nodes:
        if node in candidate:
            return candidate

    print(f"{ERROR}ERROR: could not find node containing {node} in node_containing_node in graph_collapse.py{RESET}")

    return node

def collapse_edges_repeat(old_edges: list[PathEdge|TransitionEdge]):
    new_edges = old_edges

    #repeat until new_edges stops shrinking
    while (True):
        last_edges = new_edges
        new_edges = collapse_edges(new_edges)

        print(f"collapsed {len(last_edges)} edges to {len(new_edges)}", flush = True)

        if (len(new_edges) >= len(last_edges)):
            break

    return new_edges

def collapse_edges(old_edges: list[PathEdge|TransitionEdge]):
    new_edges = []

    for edge in old_edges:
        edge.combined = False

    for U, V in pairs(old_edges):
        if not U.combined and not V.combined:
            if (type(U) == type(V)):
                if (U.start_node == V.start_node and U.end_node == V.end_node):
                    UV = create_combined_edge(U, V)
                    new_edges.append(UV)
                    U.combined = True
                    V.combined = True

    for E in old_edges:
        if not E.combined:
            new_edges.append(E)

    return new_edges

def create_combined_edge(U: PathEdge | TransitionEdge, V: PathEdge | TransitionEdge):

    if (type(U) != type(V)):
        print(f"{ERROR}ERROR: edge U type {type(U)} does not match edge V type {type(V)} in create_combined_edge in graph_collapse.py{RESET}")
        return U

    if (type(U) == TransitionEdge): #nothing to combine
        return TransitionEdge(U.start_node, U.end_node)

    if (type(U) == PathEdge and type(V) == PathEdge): #Check to enforce type

        TW = []
        OW = []
        PT = []
        NPT = []

        TW.extend(U.TW)
        OW.extend(U.OW)
        PT.extend(U.PT)
        NPT.extend(U.NPT)
        
        TW.extend(V.TW)
        OW.extend(V.OW)
        PT.extend(V.PT)
        NPT.extend(V.NPT)
        
        new_edge = PathEdge(U.start_node, U.end_node)
        new_edge.set_paths(TW, OW, PT, NPT)

        return new_edge

    print(f"{ERROR}ERROR: edge U type {type(U)} or edge V type {type(V)} is not PathEdge or TransitionEdge in create_combined_edge in graph_collapse.py{RESET}")
    return U
                
        