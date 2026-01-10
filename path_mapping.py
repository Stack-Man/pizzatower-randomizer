from node_id_objects import NodeType, StartExitType
import networkx as nx
from path_objects import Endpoint, RoomPath

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































    