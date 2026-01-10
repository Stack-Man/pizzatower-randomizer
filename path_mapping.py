from node_id_objects import NodeType, StartExitType
import networkx as nx
from path_objects import Endpoint, RoomPath
from path_traversal import flow


def layer_to_endpoints(G):
    paths = categorize_paths(G)
    ep_graph = construct_endpoint_graph(paths, None)
    
    G_init_attributes(ep_graph, paths)
    
    flowed = flow(ep_graph) #initialize flow
    
    return flowed

def G_init_attributes(G, all_paths):
    G.all_paths = all_paths
    
    G.readded_rooms = []
    G.removed_rooms = []
    
    G.removed_paths_by_room_and_endpoints = {}
    
    G.added_any_edge = False
    G.removed_any_edge = False
    
    G.removed_paths = []
    
    G.hidden_rooms = []


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

from json_to_objects import flip_dir

#TODOOOO IMPORTANT!!!! FIX THE TRANSITION MATRIX FOR NORMAL MODE!!!!!!!
def construct_endpoint_graph(paths, traversal_mode):

    endpoint_graph = nx.DiGraph()
    start_points = []
    exit_points = []
    
    for endpoint_pair, paths in paths.items():
        start_point = endpoint_pair[0]
        exit_point = endpoint_pair[1]
        
        start_points.append(start_point)
        exit_points.append(exit_point)
        
        endpoint_graph.add_edge(start_point, exit_point)
    
    #TODO: traversal mode
    #current basic traversal mode, connect directly to matching type, dir ignored
    
    #MODE: matching perfect
    #Match transitions with the same type and consistent directions
    for ep in exit_points:
        for sp in start_points:
            
            same_type = ep.door_type == sp.door_type
            good_dir = flip_dir(ep.door_dir) == sp.door_dir #flipped matches or no flip for type
            
            if same_type and good_dir:
                endpoint_graph.add_edge(ep, sp)
    
    
    #MODE: matching directional
    #Match transitions that have consistent directions, but possibly different types
    #TODO:
    
    #MODE: arbitrary no turnarounds
    #Match transitions in any way, but don't allow left/left, right/right, up/up, or down/down
    #TODO:
    
    #MODE: arbitrary no restrictions
    #Match transitions in any way
    #TODO:
    
   
    """
    for ep in exit_points:
        for sp in start_points:
            if ep.door_type == sp.door_type and ep.start_exit_type != sp.start_exit_type:
                endpoint_graph.add_edge(ep, sp)"""
    
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

#RETURN: Dict of (Start Endpoint, Exit Endpoint) as Key and a list of RoomPath as values
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
                paths[(EP_SN, EP_B)] = B.room_paths #contains all paths that lead to B
                
            else:
                ds = is_node_type(B, NodeType.DOOR, StartExitType.START)
                de = is_node_type(B, NodeType.DOOR, StartExitType.EXIT)
            
                for neighbor in G.neighbors(B):
                    
                    if ds:
                        neighbor.add_start_letter(B)
                    elif de:
                        rps = get_room_paths(G, B)
                        neighbor.add_room_paths(rps)
    
    return paths

def get_room_paths(G, N):
    room_paths = []
    
    for SL in N.start_letters:
        
        room_name = N.inner_id.room_id
        start_letter = SL
        exit_letter = N.inner_id.letter
        
        is_oneway = check_oneway_path(G, room_name, start_letter, exit_letter)
        
        rp = RoomPath(room_name, start_letter, exit_letter, is_oneway)

        room_paths.append(rp)
    
    return room_paths

import node_id_objects as nio

def check_oneway_path(G, room_name, start_letter, exit_letter):
    
    door_a_index = nio.create_door_node_id(StartExitType.START, room_name, start_letter)
    door_b_index = nio.create_door_node_id(StartExitType.EXIT, room_name, exit_letter)
    
    edge = G[door_a_index][door_b_index]
    
    if "path" in edge:
        path = edge["path"]
        return path.is_oneway
    
    return False
    

def is_node_type(node, node_type, se_type):
    return node.node_type == node_type and node.inner_id.start_exit_type == se_type































    