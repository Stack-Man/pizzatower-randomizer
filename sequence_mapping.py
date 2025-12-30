"""
For any path between two endpoints A and F
the interals of the path are irrelevant.
The only necessary qualities of the path are that its endpoints
match A and F

Consider some path from A to F, A > F
If no such direct path A > F exists
there may be some larger sequence that
bridges the gap, A > B > F

The sequence A > B > F is comprised of two subpaths
A > B and B > F
Repeat the logic used for A > F on these two subpaths
IE, A > C > B and B > D > F
Repeat the process until all subpaths terminate at some direct path between two end points

This process could be used not just to identify paths between two endpoint layers, 
but between any two rooms, allowing easier lengthening of any path.

In actuality, a path A > B > F is actually represented as two pairs of paths, A > B and B > F,
IE: (A > B) > (B > F)
B > B is unnecessary to find.
the two sub paths may grow as described
this strucure also allows arbitrary replacement,
IE: (A > B) > (D > F)
this allows different traversal modes with non-matching door types

TODO:
we may want to consider some way to grapiphy the stored path types
so we can easily swap out segments
            _ D > F
IE, A > B < _ 
              B > F
              
instead of recording A > B > D >F and A > B > B > F separately, we would record
A > B : [(D, F), (B, F)]
but we do also want to know the final length since D > F may make it longer than B > F :think:
maybe still have spearate categories for every length, so all length 3  taht us D > F and B > F wuld be in one
but all legnth 4 would use another, etc.

TODO:
do we actually want to normalize the graph with every possible combination of sequences? it could get enormous in 
some modes, such as arbitrary, imagine 10 types of exits leading to any other exit with no repeats, = 3628800 different path sequences
rather than do a full traversal, we only need to know the immediate next type we can use in the sequence?
also consider: if we find a path A > F then we have no need to find A > D > F ? well no because we want to lengthen the paths...

:thinking:

mayhaps, instead of finding all possible paths in order to know a length
we just record the immediate paths and perform actual checking to see if the path we chose works or not, IE if it eventually leads to our desired point

the problem is a flow of directed edges i want to go from A to F without entering a dead end
okay, i could have a full graph of all edges

if i want to knwo A > F
lets assume i get A > F dierctly
now i want to extend A > F

i want to be able to extend multiple rooms at a time
for example, if i did only one,
A > D > F but if no such D > f exists, then the sqeuence

A > D > B > F where A > D, D > B, and B > F exist, will never arise

need some way to identify repeated structures i nthe normalized graph and
point ot those instead of repeating alraedy known information

FOR EXAMPLE

A > B > C > D >E
and
A > G > C > D >E

ostensibly, C > D> E is a repeated sturcture
and if there are any branches from C D or E
those would be repeated too

so really the graph could look like
    B
A <   > C - D - E
    G

so i could store it like

A > [B, G] > C > D > E

lets imagine an even larger structure, seen in problem.png!

"""

#Algorithm
    #1. Categorize all paths based on endpoints
    #2. Construct graph where edges are paths and nodes are endpoint types
    #3. Connect exit nodes to matching start nodes (should we use transition matrix here?)
    #4. Perform DFS from each start node to normalize the graph. Every path can visit each node exactly once at most.
    #5. Record the final paths of the DFS, organized by length

def map_sequences(layer):
    #1. Categorize all paths based on endpoints
    endpoint_paths = categorize_paths(layer)
    
    #2. Construct graph where edges are paths and nodes are endpoint types
    #3. Connect exit nodes to matching start nodes (should we use transition matrix here?)
    endpoint_graph = construct_endpoint_graph(endpoint_paths)
    
    starting_nodes = get_start_transition_nodes(endpoint_graph)
    normalized_ep_graph = normalize_graph(endpoint_graph, starting_nodes)
    
def categorize_paths(layer):
    #1. Categorize all paths based on endpoints
    #return as dict where keys are pairs of endpoints
    #and value is a list of all paths matching that pair
        #*** IF WE WERE TO USE TRANSITION MATRIX for step 3, we would still need to redundantly categorize endpoint paths
        #In "types" they dont belong, or collapse types into single nodes
        #because otherwise when picking paths that match, wed never pick the ones that werent direct matches
        #in fact, need to do this always because of the left/right problem
        #OR DO WE?
        #if we use a transition matrix, then a path sequence from A to F may be logged as
        #A > B > D > F
        #if we imagine that B is allowed to connect to F
        #and if we only need to find path connect every second set of rooms in the path (IE a pair of start, exit)
        #then we'd onmly find (A > B) and (D> F)
        #which should match the actual and real paths only
    #TODO:
    return {}

def construct_endpoint_graph(paths):
    #2. Construct graph where edges are paths and nodes are endpoint types
    #3. Connect exit nodes to matching start nodes (should we use transition matrix here?)
    #TODO:
    return nx.DiGraph()

def get_start_transition_nodes(G):
    #4a. Get nodes == NodeType.TRANSITION and == StartExitType.START
    return []

def normalize_graph(G, start_nodes):
    #convert a directed graph with no cycles
    #into one with no converging edges
    #that is edges that point to the same node
    #though nodes can have more than one edge leading out
    #do this by creating a unique copy of a node and all the nodes after it
    #for every node that points into it
    
    #treat all starting nodes as children of "origin" node
    #to seed the algorithm
    origin = nio.create_path_node_id([], "origin")
    
    #contains pairs of nodes
    #(from, to)
    #where to is the node we're actually visiting
    #and from is a previously added node
    to_visit = [ (origin, n) for n in start_nodes ]
    
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
    
    return normalized_graph

def get_all_paths(G):
    
    #perform DFS on G and record the sequence of endpoints for every possible path
    
    
    return {}





























    