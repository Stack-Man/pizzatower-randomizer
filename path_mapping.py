from node_id_objects import NodeType, StartExitType
import networkx as nx

class Endpoint():
    def __init__(self, node):
        self.door_type = node.inner_id.door_type
        self.door_dir = node.inner_id.door_dir
        self.start_exit_type = node.inner_id.start_exit_type
        self.steps = {}
        self.next_steps = {}
        
        self.steps["NONE"] = "NONE"
    
    def __str__(self):
        return f"{self.door_type} {self.door_dir}"
    
    def __eq__(self, other):
        return self.door_type == other.door_type and self.door_dir == other.door_dir and self.start_exit_type == other.start_exit_type
    
    def __hash__(self):
        return hash((self.door_type, self.door_dir, self.start_exit_type))

def paths_to_endpoints(G):
    paths = categorize_paths(G)
    ep_graph = construct_endpoint_graph(paths, None)
    
    return ep_graph

"""
------------------
STRUCTURE OF GRAPH
------------------
Construct a directed bipartite graph with two sets: Start Endpoints and Exit Endpoints
Start > Exit edges represents all paths with those types of endpoints
Exit > Start edges represent edges in the transition matrix

The Transition Matrix is a graph showing which start endpoints an exit endpoint 
is allowed to lead to in the next room
"""

def construct_endpoint_graph(paths, traversal_mode):

    endpoint_graph = nx.DiGraph()
    start_points = []
    exit_points = []
    
    for endpoint_pair in paths.keys():
        start_point = endpoint_pair[0]
        exit_point = endpoint_pair[1]
        
        start_points.append(start_point)
        exit_points.append(exit_point)
        
        endpoint_graph.add_edge(start_point, exit_point)
    
    #TODO: traversal mode
    #current basic traversal mode, connect directly to matching type, dir ignored
    
    for ep in exit_points:
        for sp in start_points:
            if ep.door_type == sp.door_type and ep.start_exit_type != sp.start_exit_type:
                endpoint_graph.add_edge(ep, sp)
    
    return endpoint_graph


"""
------------------------------------
ALGORITHM - CATEGORIZE PATHS BY TYPE
------------------------------------
Traverse the Transition > Door > Transition Graph
To collect paths and categorize them by the pair 
of their start and exit transitions

1. Store all start nodes in S
2. For every node SN in S
3. Perform BFS from SN
4. For every node B from BFS
5. For every neighbor N of B

6a. If B is START DOOR: append B.letter to N.start_letters
6b. Else if B is EXIT DOOR: for every start letter SL in B.start_letters append (room name, B.letter and SL) to B.paths
6c. Else if B is EXIT TRANSITION set paths_by_type[(SN, B)] = B.paths

"""
def BFS(G, start_node):

    visited = []
    to_visit = []
    plan_visit = [start_node]
    
    while len(plan_visit) > 0:
        
        to_visit = plan_visit
        plan_visit = []
    
        for n in to_visit:
            
            if n not in visited:
                visited.append(n)
                
                yield n
                
                for neighbor in G.neighbors(n):
                    plan_visit.append(neighbor)

def categorize_paths(G):
    
    start_nodes = []
    paths = {}
    
    for N in G.nodes():
        if is_node_type(N, NodeType.TRANSITION, StartExitType.START):
            start_nodes.append(N)
            
    for SN in start_nodes:
        
        EP_SN = Endpoint(SN)
        
        for B in BFS(G, SN):
            
            #Collect start door letters in exit doors
            #Then collect name + letter paths in exit transitions
            #Then transfer those stored paths to the dictionary
            if is_node_type(B, NodeType.TRANSITION, StartExitType.EXIT):
                
                EP_B = Endpoint(B)
                paths[(EP_SN, EP_B)] = B.room_paths
                
            else:
                ds = is_node_type(B, NodeType.DOOR, StartExitType.START)
                de = is_node_type(B, NodeType.DOOR, StartExitType.EXIT)
            
                for neighbor in G.neighbors(B):
                    
                    if ds:
                        neighbor.add_start_letter(B)
                    elif de:
                        neighbor.add_room_paths(B)
    
    return paths


def is_node_type(node, node_type, se_type):
    return node.node_type == node_type and node.inner_id.start_exit_type == se_type































    