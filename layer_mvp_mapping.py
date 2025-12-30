"""
Construct Minimum Viable Paths (MVPs) between two end point layers.
MVPs are paths with no redundant exits.
A redundant exit is one that previously exists in the path.
An exit is any node marked as "transition, exit"

Algorithm:
	For all exit transition nodes:
	1. Flow forward along each path.
	1b. Terminate and remove redundant edges
    1c. record all end points of the paths
	
	For all final paths:
	2. Flow backwards from end of paths
	2b. Terminate if path ends at exit transition node
	2c. Remove edge if there are no other neighbors to the edge start (IE, possibly supporting another path)
"""

from node_id_objects import NodeType, StartExitType
import node_id_objects as nio
import networkx as nx
import copy

def construct_mvp_layer(start_layer, inbetween_layer, exit_layer):
    
    current_round = 0
    path_ends = []
    next_path_ends = []
    
    #populate path_ends with start_layer exit transition nodes
    
    #add start layer to mvp layer
    #add exit layer to mvp layer
    #connect path ends to start paths of exit layer using transition matrix
    
    mvp_layer = nx.DiGraph()
    mvp_layer.update(start_layer)
    mvp_layer.update(exit_layer)
    
    starting_nodes = get_exit_nodes(start_layer)
    
    #TODO: connect starting nodes to start transition nodes ofe xit layer using transition matrix
    
    #TODO copy loop adn check if need new copy of graph or finished with all flows
    
    mvp_layer.update(inbetween_layer)
    path_ends = traverse_forward(start_nodes, mvp_layer)
    
    #TODO: connect path ends to start transition nodes ofe xit layer using transition matrix
    
    
    #add first inbetween layer
    #for each path end
        #connect to start paths of inbetween layer using transition matrix
    
    #for each path end
        #depth first search
        #for every neighbor
            #if neighbor is exit transition
                #if neighbor is redundant in curr_path
                    #remove edge(curr, neighbor)
                    #next_path_ends.append(curr)
                #else
                    #curr_path
                    #neighbor.curr_path.append(neighbor)
                    #next_path_ends.append(neighbor)
                    
            #else
                #flow forward(neighbor)
    
    #for each next path end
        #backwards depth first search
        #if note xit transtiion
            #remove (self, prev)
            #flow backward(prev)

def traverse_forward(start_nodes, layer):
    
    to_vist = start_nodes
    path_ends = []
    
    #populate paths with self as the first exit
    for node in to_visit:
        node.path = [node]
    
    #TODO TODO:redundancy rule may remoev edge used by other possible path
    #need to determine where exactly we hould remove the edge
    #C-A-\
    #    |-C
    #D-B-/
    #in this scenario removing |-C would disable the path for D-B even though
    #D-B doesnt have a redundant exit
    #but we also need to account for all possible branch points, so where would
    #we remove the edge to disable the redundant path?
    
    #depth first search of rest of layer
    while len(to_visit) > 0:

        current_node = to_vist.pop()

        for neighbor in current_node.neighbors():
            
            #reached end, dont set current node
            if is_exit_transition(neighbor):
                if is_redundant_exit(current_node.path, neighbor):
                    layer.remove_edge(current_node, neighbor)
                    path_ends.append(current_node)
                else
                    neighbor.path = current_node.path.copy()
                    neighbor.path.append(neighbor)
                    path_ends.append(neighbor)
            
            #not end, continue flow forward
            else:
                neighbor.path = current_node.path
                #don't add self because the path is only a list of exits
                to_vist.append(neighbor) #add immediately, DFS #TODO: doesnt check for previous visited so will haev many duplicates

    return path_ends

def normalize_graph(G, start_nodes):
    #convert a directed graph with no cycles
    #into one with no converging edges
    #that is edges that point to the same node
    #though nodes can have more than one edge leading out
    #do this by creating a unique copy of a node and all the ndoes after it
    #for every node that points into it
    
    #treat all starting nodes as children of "origin" node
    #to seed the algorithm
    origin = nio.create_path_node_id([], "origin")
    
    #contains pairs of nodes
    #(from, to)
    #where to is the node we're actually visiting
    #and from is a previously added node
    to_visit = [ (origin, n) for n in start_nodes ]
    
    #visited is pairs of nodes
    #the visited node and the node it was visited from
    #this allows repeat visits of nodes if it is being visited from
    #a different node
    #visited = []
    
    #latest copies contains the most recent copy of
    #a node added to the graph
    #this lets us track which copy of a node we want to connect an edge to
    #as only the most recent copy  will ever have new edges
    #added to it
    latest_copies = {}
    
    #initialize the graph with the origin node
    normalized_graph = nx.DiGraph()
    normalized_graph.add_node(origin)
    latest_copies["origin"] = origin
    
    #TODO: do we even need a visited list or have any need to check it?
    #the to_visit list seems to keep track of everything
    #and we can never visit the same pair twice, wait actually we even WANT to check the same pair twice
    #TODO TODO: remove visited check! for example (blue, purple) appears twice and we want both!
    #because there are no cycles, a comprehensive visited check is unnecessary
    
    
    while len(to_visit) > 0:
        
        current_pair = to_visit.pop()
        
        #if current_pair not in visited:
        if True:
            #visited.append(current_pair)
            
            prev_node = current_pair[0]
            current_node = current_pair[1]
            
            #get path up to this node
            prev_path_node = latest_copies[prev_node]
            
            #copy path and add self to path
            current_path = prev_path_node.path.copy()
            current_path.append(current_node)
            
            #create path node out of path and this ndoe
            path_node = nio.create_path_node_id(current_path, current_node)

            #add edge to the graph
            normalized_graph.add_edge(prev_path_node, path_node)

            #record latest copy for later reference
            latiest_copies[current_node] = path_node
        
            #mark all neighbors of this node to visit
            for neighbor in G.neighbors(current_node):
                neighbor_pair = (current_node, neighbor)
                
                
                #if neighbor_pair not in visited:
                if True:
                    to_visit.append(neighbor_pair)
    
    #use pairs of visited nodes to construct graph
    #each pair represents (start of edge, new node as new edge)
    #use the path to the node as part of the index to make it unique
    
    #TODO: how do i differentiate which node is the one to start the edge at?
    #maybe just most recent one that matches?
    #how do i find it if i dont know the path?
    #for any specific node N store a reference to its most recent copy added and use that (so a dict look up)
    #well no because if im going over it after the fact that wont work
    #perhaps i should construct the graph during the DFS?
        

def create_normalized graph
    
def is_exit_transition(node):
    return node.type == NodeType.TRANSITION and node.inner_id.start_exit_type == StartExitType.EXIT

def is_redundant_exit(path, check_node):
    for exit_node in path:
        if exit_node.inner_id.door_type == check_node.inner_id.door_type and exit_node.inner_id.door_dir == check_node.inner_id.door_dir:
            return True
    
    return False

def copy_graph(G, id):
    
    new_G = copy.deepcopy(G)
    new_G["layer_id"].id = id
    
    return new_G
    
def get_exit_nodes(G):
    
    exit_nodes = []
    
    for node in G.nodes():
        if is_exit_transition(node):
            exit_nodes.append(nodes)
    
    return exit_nodes
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    