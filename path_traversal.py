import networkx as nx
from node_id_objects import StartExitType

"""
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

1. For each neighbor N of A
3. If N[F] = A[F] - 1 then set A = N and goto step 1 
3b. Choose path P of room R, then remove all paths of room R from graph and reflow if any edges become disconnected
4. Else If N[F] = 0, end
"""

#RETURN: List of (Endpoint, Path) for every chosen Endpoint and their related path
#EXIT endpoints have Path set as None
def find_path(G, all_paths, A, F):

    chosen_endpoints = []
    
    
    if F not in A.steps:
        print("FAIL! no path from A to F")
        return None
    
    print(" start at " + str(A)  + " A[F] = " + str(A.steps[F]))
    
    while not A == F: #N[F] == 0
    
        for N in G.neighbors(A):
            if F in N.steps and N.steps[F] == A.steps[F] - 1:
                
                print(" to " + str(N) + " N[F] = " + str(N.steps[F]))
                
                chosen_path = None
                
                if A.start_exit_type == StartExitType.START:
                    chosen_path = choose_path(G, all_paths, A, N)
                    
                chosen_endpoints.append((A, chosen_path))
 
                A = N
                
                break #to next while loop
    
    chosen_endpoints.append((F, None)) #If F is START, assume it is being appended to some already existing path choice

    return chosen_endpoints

def choose_path(G, all_paths, A, F): #TODO: check if we need path or not
    
    paths_of_types = all_paths[(A, F)]
    path = paths_of_types[0]
    
    remove_all_room_paths(G, path, all_paths)
    
    return path

"""
---------------------------------------------------------------
ALGORITHM - FIND A[N] (STEPS FOR A TO REACH N) FOR ALL N (FLOW)
---------------------------------------------------------------
1. For every node N in G, N[N] = 0
2. For every node N
3. For every reverse neighbor RN of N
4. RN[N] = N[N]

For Step 2, use concurrency to process every node N simultaneously.
Locks are unnecessary if we keep all threads synced per round R
In any round R, N[N] = R 
therefore no node N can write any value other than R to RN[N]
therefore, there can be no conflict if no thread starts round R + 1
before all threads finish round R
"""

import threading
round = 0
added_this_round = False
def set_add_true():
    global added_this_round
    added_this_round = True
    #print("SET ADD TRUE")

def set_add_false():
    global added_this_round
    added_this_round = False
    #print("SET ADD FALSE")

def flow(G): 
    global round
    global added_this_round
    
    #initial seed
    #empty the dicts and set 0 steps to self
    for N in G.nodes():
        N.steps = {}
        N.steps[N] = 0
        N.next_steps = {}

        
    round = 0
    GR = G.reverse()
    
    while (True):
        round = round + 1
        #print("Flow round " + str(round))
        
        pass_values_from_all(GR) #flow backwards
        
        set_add_false()
        
        #finalize all new steps only after
        #all threads in round finished
        #print("add new to all")
        add_new_to_all(GR)

        
        if not added_this_round:
            #print("break not added this round")
            break #end when no new steps flowed back
        
    return GR.reverse()

def add_new_to_all(GR):
    threads = []
        
    #move next steps to steps
    for N in GR.nodes():
        t = threading.Thread(target=add_new, args=(N, ))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

def pass_values_from_all(GR):
    threads = []
        
    #flow all steps in N to all of its reverse neighbors
    for N in GR.nodes():
        t = threading.Thread(target=pass_values, args=(GR, N))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

def add_new(N):
    curr = N.steps
    next = N.next_steps

    for key, value in next.items():
        if key not in curr:
            curr[key] = value
            set_add_true()
            #print("     ADDED THIS ROUND")
        #else:
            # print(f"   {N}[{key}] < {value} already there")
    
    N.steps = curr
    N.next_steps = {}

def pass_values(GR, N):
    global round
    
    #print(f"Passing N's steps to reverse neighbors")
    
    for RN in GR.neighbors(N):
        to_add = N.steps
        
        #current round should always match
        #value + 1
        for K in to_add:
            RN.next_steps[K] = round
            #print(f"    Added {RN}[{N}] = {round}")

"""
--------------------------
GROWING A PATH FROM A TO F
--------------------------
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
1. With path AF of length N choose X, Z from [0, N] where Z > X
2. For at least one neighbor N of X, Y = X + 1, find at least one path NZ where N != Y and N[Z] >= X[Z]

3a. If such a path exists
4a. Find Path YZ
5a. for every room R of path P in AF, readd P to G
6a. If at least one new edge P is added to G, flow G

3b. Else move X and Z and goto step 2
"""
import random

def grow_path(G, all_paths, endpoint_path):
    
    XZs = []
    i_F = len(endpoint_path) - 1
    
    while (True):
        #TODO: seeded randomization
        #and exhaustive picking of ids
        #could initialize X and Z then with every failurei ncrement X until it reaches Z at which point
        #we reset X and increment Z then repeat
        i_X = random.randint(0, i_F - 1) #A <= X < Z <= F therefore X <= F - 1
        i_Z = random.randint(i_X + 1, i_F)
        
        print("Grow segment " + str(endpoint_path[i_X][0]) + " to " + str(endpoint_path[i_Z][0]))
        
        X = endpoint_path[i_X][0]
        Y = endpoint_path[i_X + 1][0]
        Z = endpoint_path[i_Z][0]
        
        #temp add removed paths to check for new path
        #TODO: probably need to account fo thef act that removed rooms is global...
        #have to add the unadd instead of making a copy of G
        path_XZ = get_endpoint_path_segment(endpoint_path, i_X, i_Z - 1) #include X because it is old XY, exclude Z because it will be kept for ZF
        add_all_room_paths(G, path_XZ, all_paths) #temp readd old paths from XZ
        
        N = check_for_new_path(G, X, Y, Z)
        
        if N:
            
            #find separately to force our path down N instead of Y
            path_XN = find_path(G, all_paths, X, N)
            path_NZ = find_path(G, all_paths, N, Z)

            path_AX = get_endpoint_path_segment(endpoint_path, 0, i_X - 1) #exclude X because X is part of XN
            path_XN = get_endpoint_path_segment(path_XN, 0, len(path_XN) - 2) #include X, exclude N because N is part of NZ(-2 bc len is + 1)
            path_NZ = get_endpoint_path_segment(path_NZ, 0, len(path_NZ) - 2) #include N, exclude Z because it is part of ZF (-2 bc len is + 1)
            path_ZF = get_endpoint_path_segment(endpoint_path, i_Z, i_F)   #include Z because Z from NZ does not have a room picked
            
            path_AXNZF = reconstruct_endpoint_path_from_segments([path_AX, path_XN, path_NZ, path_ZF])
            
            return path_AXNZF #TODO: report size of increase
        else:
            
            #re-remove the used paths
            remove_all_endpoint_path_room_paths(G, all_paths, endpoint_path)
            
            print("==========FAILED TO GROW!!!!")
            
            return endpoint_path #TODO: report size of increase (0)

def print_path(path):
    print("path: ")
    for S in path:
        print(f"    {str(S[0])} via {str(S[1])} > ")

def check_for_new_path(G, X, Y, Z): #TODO: include target size?
    
    for N in G.neighbors(X):
        #print("     Check for new path to Z:" + str(Z) + " from N:" + str(N))
        
        """
        if N is Y:
            print("         Fail, N is Y")
        elif Z not in N.steps:
            print("         Fail, Z not in N")
            
            for K, V in N.steps.items():
                print(f"            {K}:{V}")
        elif not N.steps[Z] >= X.steps[Z]:
            print("         Fail, N < Z")
        """
        
        if N is not Y and Z in N.steps and N.steps[Z] >= X.steps[Z]:
            return N
    
    return None

#inclusive both ends
def get_endpoint_path_segment(endpoint_path, i_start, i_end):
    
    if i_end < i_start:
        return []
    
    segment = []
    
    i_next = i_start
    
    while i_next <= i_end:
        
        segment.append(endpoint_path[i_next])
        i_next = i_next + 1
    
    return segment

def reconstruct_endpoint_path_from_segments(segments):
    path = []
    
    for segment in segments:
        for item in segment:
            path.append(item)
    
    return path

"""
--------------------------
ADD OR REMOVE PATHS FROM G
--------------------------

If we use some path P from room R all other paths in R become unavailable.
Similarly, if we choose not to use said path, the paths of R become available again.

In any shortest path AF, as long as one valid path P for each edge remains, the path is valid.
If we use all paths of edge XY in AF, we must remove edge XY from the graph
This removal changes the shortest paths for any path AF, so we must reflow the graph.

And vice versa if we add some edge XY to G

---------------------------------------
ALGORITHM - REMOVE PATHS OF ROOM FROM G
---------------------------------------
1. Get Room R of path P
2. For every category of paths AF
3. Remove all paths R_P in all_paths[AF]
3b.Store all removed paths in dict[R][AF] for later readdition
4. If all_paths[AF] = 0, remove AF from G
5. If at least one edge was removed, Flow(G)
"""

removed_any_edge = False
removed_paths = []
removed_paths_by_room_and_endpoints = {}

def remove_all_endpoint_path_room_paths(G, all_paths, endpoint_path):
    
    for endpoint_path_pair in endpoint_path:
        path = endpoint_path_pair[1]
        
        if path:
            remove_all_room_paths(G, path, all_paths)

def remove_all_room_paths(G, path, all_paths):
    global removed_any_edge
    global removed_paths
    
    room_name = path.room_name
    removed_any_edge = False
    removed_paths = []
    
    threads = []
    
    for endpoint_pair, paths in all_paths.items():
        t = threading.Thread(target=remove_room_paths, args=(endpoint_pair, room_name, paths, G, all_paths))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    if removed_any_edge:
        G = flow(G)
    
    global removed_paths_by_room_and_endpoints
    
    removed_paths_by_room_and_endpoints[room_name] = {}
    
    #Store removed paths by room then by endpoint
    for endpoint_pair_and_path in removed_paths:
        
        endpoint_pair = endpoint_pair_and_path[0]
        path = endpoint_pair_and_path[1]
    
        
        if endpoint_pair not in removed_paths_by_room_and_endpoints[room_name]:
            removed_paths_by_room_and_endpoints[room_name][endpoint_pair] = [path]
        else:
            removed_paths_by_room_and_endpoints[room_name][endpoint_pair].append(path)
        

def remove_room_paths(endpoint_pair, room_name, paths, G, all_paths):
    global removed_any_edge
    global removed_paths
    
    new_paths = []
        
    for P in paths:
        if not P.room_name == room_name:
            new_paths.append(P)
        else:
            #store removed path as its endpoint pair and the path
            removed_paths.append((endpoint_pair, P))
    
    all_paths[endpoint_pair] = new_paths
    
    if len(new_paths) == 0 and G.has_edge(endpoint_pair[0], endpoint_pair[1]): #threading check, dont remove edge if already removed, maybe could check original length instead?
        G.remove_edge(endpoint_pair[0], endpoint_pair[1])
        removed_any_edge = True

added_any_edge = True
"""
---------------------------------------
ALGORITHM - ADD PATHS OF ROOM FROM G
---------------------------------------
1. For every room R in path AF
2. For every removed path P of type XY from R
3. add P to all_paths[XY]
4. if all_paths[XY] WAS 0, add edge XY to G
5. If at least one edge was added, Flow(G)
"""


def add_all_room_paths(G, endpoint_path, all_paths):
    global added_any_edge
    
    added_any_edge = False
    threads = []
    used_room_names = []
    
    for endpoint_and_path in endpoint_path:
        
        path = endpoint_and_path[1]
        
        #if the endpoint has an associated RoomPath
        if path: 
            room_name = path.room_name
            
            if room_name not in used_room_names: #prevent multiple threads for the same room from being created
                used_room_names.append(room_name)
                
                t = threading.Thread(target=add_room_paths, args=(room_name, G, all_paths))
                threads.append(t)
                t.start()
    
    for t in threads:
        t.join()
    
    if added_any_edge:
        G = flow(G)

def add_room_paths(room_name, G, all_paths):
    global removed_paths_by_room_and_endpoints
    global added_any_edge
    
    if room_name in removed_paths_by_room_and_endpoints:
        removed_paths_by_endpoint = removed_paths_by_room_and_endpoints[room_name]
        
        for endpoint_pair, paths in removed_paths_by_endpoint.items():
            original_length = len(all_paths[endpoint_pair])
            all_paths[endpoint_pair] = paths
            
            if (original_length == 0):
                G.add_edge(endpoint_pair[0], endpoint_pair[1])
                added_any_edge = True
        
        del removed_paths_by_room_and_endpoints[room_name]

