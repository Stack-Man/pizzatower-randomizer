"""
---------------------------------------
STRUCTURE OF GRAPH
---------------------------------------
Construct a directed bipartite graph with two sets: Start Endpoitnts and Exit Endpoints
Start > Exit edges represents all paths with those types of endpoints
Exit > Start edges represent edges in the transition matrix

The Transition Matrix is a graph showing which start endpoints and exit endpoint 
is allowed to lead to in the next room


---------------------------------------
FINDING A PATH FROM A TO F
---------------------------------------
For any path between two endpoints A and F
the internals of the path are irrelevant.

Consider identifying some path from A to F
The shortest path from A to F is n steps long
The next node in this path after A is n-1 steps away from F

From node A n steps away from F move to any neighbor node that is n-1 steps away from F
Repeat until F is 0 steps away (on F)

----------------------------
ALGORITHM - FIND PATH A TO F
----------------------------
Assume every node contains a dictionary storing the shortest number of steps to every node
The number of steps to reach node F from A is written as A[F]

1. Look at A[F]
2. For each neighbor N of A
3. If N[F] = A[F] - 1 then set A = N and goto step 1 
3b.Choose path P of room R, then remove all paths of room R from graph and reflow if any edges become disconnected
4. Else If N[F] = 0, end


-------------------------------
ALGORITHM - FIND A[N] FOR ALL N (FLOW)
-------------------------------
1. For every node N, N[N] = 0
2. For every node N
3. For every reverse neighbor R of N
4. R[N] = Min( N[N], R[N]

For Step 2, use concurrency to process every node N simultaneously.
Use Locks before read to prevent simultaneous reads to ensure only the lowest value is written.
Should a thread encounter a lock, remember that node and come back to it later. proceed to the next reverse neighbor R2

ACTUALLY is such a lock needed?
in round R all nodes pass back steps of length R
therefore, there is no need to care what order the nodes in round R read and write
as all nodes writing step R[N] will be doing so with the same value of N[N]
what IS Necessary is that all threads are synced to rounds
so upon reaching the end of a round, wait until all theads are ready to continue

---------------------------------------
GROWING A PATH FROM A TO F
---------------------------------------
For any path between two endpoints A and F
with N steps across nodes from S0 to SN where A = S0 and F = SN ( S0 > S1 > S2 ... SN-1 > SN )
any segment from any node SX in that path to any node after it SY where Y > X
can be replaced with some path SG > SH such that the length of SGH is larger than SXY

From node SX, look at the remaining steps to SY
choose some neighbor of SX, SP such that SP[SY] = SX[SY] - 1
AND such that SP != SX+1 (the node originally after X)

By choosing SX and SY randomly we are able to possibly create ANY sequence of rooms
For example (without length increasing)
XABY > XDEY if SX = X and SY = Y
XABY > XACY if SX = A and SY = Y

The initial path of length N takes priority over any other path of the same length N
If we randomize the order of paths in the graph, we can have the ability to choose different
initial paths as well. Therefore, there is no concern of always choosing the same length paths
in the same order.


--------------------------------------
ALGORITHM - GROW LENGTH OF PATH A TO F
--------------------------------------
1. For path AF of length N choose X, Y from [0, N] where Y > X
2. For at least one neighbor of X, look for at least one path XY where X + 1 in XY != X + 1 in AF and X+1[Y] >= X[Y]

3a. If such a path exists: For each room R of every path P in segment X to Y readd all paths from room R to the graph and reflow if any new edges were added
4a. Find Path XY where X + 1 in XY != X + 1 in AF and X+1[Y] >= X[Y]

3b. Else move X and Y and goto step 2
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






























    