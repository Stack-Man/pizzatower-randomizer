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
"""

from node_id_objects import NodeType, StartExitType

class Endpoint():
    def __init__(self, node):
        self.door_type = node.inner_id.door_type
        self.door_dir = node.inner_id.door_dir
    
    def __str__(self):
        return f"{self.door_type} {self.door_dir}"
    
    def __eq__(self, other):
        return self.door_type == other.door_type and self.door_dir == other.door_dir
    
    def __hash__(self):
        return hash((self.door_type, self.door_dir))

class RoomPath():
    def __init__(self, room_name, start_letter, exit_letter):
        self.room_name = room_name
        self.start_letter = start_letter
        self.exit_letter = exit_letter

def categorize_paths(G):
    #Categorize all paths based on endpoints
    #return as dict where keys are pairs of endpoints
    #and value is a list of all paths matching that pair
    
    
    #get transition, start nodes
    #for every start node
        #perform DFS
        #upon reaching an exit
        #record dict[(start, exit)] = (room, start door, exit door)
    
    start_nodes = []
    paths_by_type = {}
    
    for node in G.nodes():
        if is_node_type(node, NodeType.TRANSITION, StartExitType.START):
            start_nodes.append(node)
    
    for sn in start_nodes:
        
        start_point = Endpoint(sn)
        to_visit = [sn]
        
        while len(to_visit) > 0:
            
            current_node = to_visit.pop()
            
            if is_node_type(current_node, NodeType.TRANSITION, StartExitType.EXIT):
                
                exit_point = Endpoint(current_node)
                key = (start_point, exit_point)
                paths = current_node.room_paths
                
                #doesnt matter if there is already a key existing
                #because the most recent one should include all previous paths
                #maybe would have been better to do a BFS instead 
                #to prevent that but here we are
                paths_by_type[key] = paths
                    
            else:
                
                is_start_door = is_node_type(current_node, NodeType.DOOR, StartExitType.START)
                is_exit_door = is_node_type(current_node, NodeType.DOOR, StartExitType.EXIT)
                
                for neighbor in G.neighbors(current_node):
                    to_visit.append(neighbor)
                    
                    #send start letter to neighbor (exit door)
                    if is_start_door:
                        neighbor.add_start_letter(current_node.inner_id.letter)
                    
                    #send all room paths to neighbor (exit transition)
                    if is_exit_door:
                        room_name = current_node.inner_id.room_id
                        exit_letter = current_node.inner_id.letter
                        
                        #every start door leading to this exit door 
                        for start_letter in current_node.start_letters:
                            room_path = RoomPath(room_name, start_letter, exit_letter)
                            neighbor.add_room_path(room_path)
    
    return paths_by_type

def is_node_type(node, node_type, se_type):
    return node.node_type == node_type and node.inner_id.start_exit_type == se_type

def construct_endpoint_graph(paths_by_type, traversal_mode):
    #Construct directed bipartite graph where edges are paths and nodes are endpoint types
    #Connect exit nodes to matching start nodes using transition matrix
    #TODO:
    
    endpoint_graph = nx.DiGraph()
    start_points = []
    exit_points = []
    
    for endpoint_pair in my_dict.keys():
        start_point = endpoint_pair[0]
        exit_point = endpoint_pair[1]
        
        start_points.append(start_point)
        exit_points.append(exit_point)
        
        endpoint_graph.add_edge(start_point, exit_point)
    
    #TODO: traversal mode
    #current basic traversal mode, connect directly to matching type, dir ignored
    
    for ep in exit_points:
        for sp in start_points:
            if ep.door_type == sp.door_type:
                endpoint_graph.add_edge(ep, sp)
    
    return endpoint_graph






























    