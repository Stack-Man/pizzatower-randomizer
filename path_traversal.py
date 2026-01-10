import networkx as nx
from node_id_objects import StartExitType
from copy import deepcopy

"""
=====================================
CREATING PATHS BETWEEN ENDPOINT ROOMS
====================================

When picking endpoint rooms (Branch, Entrance, John) we can't be sure which combination of two endpoints
has a valid path that can be created between them. Additionally, its possible some valid path was consumed
by a previous set of endpoints that didn't necessarily NEED to use it.

To resolve this issue we do two things:

1. Pass all possible endpoints for a segment and exhaustively try paths between combinations of them
2. Prioritize edges that have MORE than one remaining path in that path type.

The latter means that we don't need to deconstruct and rebuild segments to use an edge that segment
consumed because it is unlikely to have consumed said edge in the first place.

(Technically, this can still occur. If segment AB consumes N1 and there is segment CD NEEDS N2, then some segment FE that NEEDS N1 or N2
will not ask AB to release N1 and AB is not prohibited from consuming it. But doing an exhaustive check to
resolve this is hard to code and probably computationally expensive)

"""

def create_bridge_twoway(G, As, Fs): #As and Fs should be lists of types inheriting BaseRoom
    
    print("Try Bridge Twoway")
    
    def twoway_endpoint_extractor(A):
        return A.get_twoway_endpoint()

    chosen_A, chosen_F, twoway_path_AF = find_some_path_with_unhides(G, As, Fs, endpoint_extractor = twoway_endpoint_extractor, prioritize_oneway = False)
    
    return chosen_A, chosen_F, twoway_path_AF

def create_bridge_oneway(G_NPT, G_PT, BSs, BEs): #BSs and #BEs should be lists of type BranchRoom
    
    print("Try Bridge Oneway")
    
    chosen_BS, chosen_BE, oneway_path_NPT, oneway_path_PT = find_some_branch_paths_with_unhides(G_PT, G_NPT, BSs, BEs)
    
    return chosen_BS, chosen_BE, oneway_path_NPT, oneway_path_PT 

def default_extractor(A):
    return A

"""
=======================================
ALGORITHM - FIND SOME PATH WITH UNHIDES
=======================================
1a. K = 0
1b. For every unordered combination of K hidden rooms in G (N choose K)
2.      Find some path with those rooms unhidden
3. If failed, K +=1 and repeat
"""

def find_some_path_with_unhides(G, As, Fs, endpoint_extractor = default_extractor, prioritize_oneway = False):
    
    print("     Find Path Unhides")
    
    max_unhidden_rooms_at_once = len(G.hidden_rooms)
    room_count_to_unhide_this_round = 0
    
    while (room_count_to_unhide_this_round <= max_unhidden_rooms_at_once):
        
        print("         Try unhide round ", room_count_to_unhide_this_round)
        
        #try to find a path with every unique combination of hidden rooms unhidden
        #when successful, replace G with that created G
        for room_combination in choose(G.hidden_rooms, room_count_to_unhide_this_round):
            
            print("             try choose combination")
            
            temp_G = deepcopy(G)
            #temp_G = G #TODO: figure out if deepcopy is messing it up
            unhide_rooms(temp_G, room_combination)
            
            print("         Find from As to Fs")
        
            chosen_A, chosen_F, path_AF = find_some_path(temp_G, As, Fs, endpoint_extractor, prioritize_oneway)
            
            if path_AF is not None:
                G = temp_G
                return chosen_A, chosen_F, path_AF
        
        room_count_to_unhide_this_round = room_count_to_unhide_this_round + 1 #try next round with more unhidden rooms
    
    #failed
    print("     Failed to find some AF with unhides")
    return None, None, None

"""
===============================================
ALGORITHM - FIND SOME BRANCH PATH WITH UNHIDES
===============================================
1a. K = 0
1b. For every unordered combination of K hidden rooms in G (N choose K)
2.      Find some NPT path with those rooms unhidden
3.          IF sucessful, use chosen A, F and curernt unhidden rooms to find PT path
4.  If failed, K += 1 and repeat
"""
def find_some_branch_paths_with_unhides(G_PT, G_NPT, BSs, BEs):
    #Assum As and Fs are lists of BranchRoom
    
    print("     Find Branch Path Unhides")
    
    max_unhidden_rooms_at_once = len(G_NPT.hidden_rooms)
    room_count_to_unhide_this_round = 0
    
    def branch_extractor_NPT(A):
        return A.NPT_endpoint
    
    def branch_extractor_PT(A):
        return A.PT_endpoint
    
    while (room_count_to_unhide_this_round <= max_unhidden_rooms_at_once):
        
        print("         Try branch unhide round ", room_count_to_unhide_this_round)
        
        #try to find a path with every unique combination of hidden rooms unhidden
        #when successful, replace G with that created G
        for room_combination in choose(G_NPT.hidden_rooms, room_count_to_unhide_this_round):
            
            print("             Try unhide room combo for branch NPT ", room_combination)
            
            #First try to find NPT
            temp_G_NPT = deepcopy(G_NPT)
            unhide_rooms(temp_G_NPT, room_combination)
            
            print("             Find from BSs to BEs")
            chosen_BS, chosen_BE, path_NPT = find_some_path(G_NPT, BSs, BEs, endpoint_extractor = branch_extractor_NPT, prioritize_oneway = True)
            
            #Then try to find PT with this NPT
            if path_NPT is not None:
                temp_G_PT = deepcopy(G_PT) #temp_G_PT will be overriden by the next func if successful
                unhide_rooms(temp_G_PT, room_combination) #unhide the rooms unhidden by this successful NPT
            
                #try find path with unhides, uses a G, F, and A  based on the current NPT
                _, _, path_PT = find_some_path_with_unhides(temp_G_PT, [chosen_BE], [chosen_BS], endpoint_extractor = branch_extractor_PT, prioritize_oneway = True)
                
                if path_PT is not None: #successful, replace Gs and exit
                    G_PT = temp_G_PT
                    G_NPT = temp_G_NPT
                    
                    return chosen_BS, chosen_BE, path_NPT, path_PT
    
        room_count_to_unhide_this_round = room_count_to_unhide_this_round + 1 #try next round with more unhidden rooms
    
    print("     Failed to find some BRANCH AF with unhides")
    return None, None, None, None

#yield every unordered combo of items
def choose(items, k):
    
    print("     Choose ", k, " items from ", items)
    
    if k <= 0:
        yield []
    elif k == 1:
        for i in items:
            yield [i]
    else:
        for x, i in enumerate(items):
            
            items_after_i = items[x+1:]
            
            for rest in choose(items_after_i, k - 1):
                yield rest.append(i)

"""
---------------------
FIND SOME PATH A TO F
----------------------
Some lists of likely BaseRooms As and Fs
For every combination of them, try to find a path AF
Extract from room Au and Fu the endpoints A and F to use, depending on AF_extractor

return the combination selected Au, Fu and the path path_AF found between them.
"""
def find_some_path(G, As, Fs, endpoint_extractor = default_extractor, prioritize_oneway = False):

    print("             Find some path in AF")

    for Au in As:
        
        A = endpoint_extractor(Au)
        
        print("                 TRY Find from ", str(A))
            
        for Fu in Fs:
        
            F = endpoint_extractor(Fu)
            
            print("                    to ", str(F))
            
            path_AF = find_path(G, A, F, prioritize_oneway)
            
            
            
            if path_AF is not None:
                return Au, Fu, path_AF
            else:
                print("                     None from ", str(A), " to ", str(F))
    
    print("             exhausted all A, F")
    
    #Exhausted all AF combos with G
    return None, None, None
    
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
from draw_test import draw_tree
from path_objects import Endpoint
from layer_objects import FakeNode

def get_endpoint(type, dir, se_type):
    n = FakeNode(type, dir, se_type)
    return Endpoint(n)

#RETURN: List of (Endpoint, Path) for every chosen Endpoint and their 
#related path EXIT endpoints have Path set as None
def find_path(G, A2, F, prioritize_oneway = False):

    chosen_endpoints = []
    
    G = flow(G) #TODO: for some reason some action is failing to flow and the values get messed up, the values to self are not 0 and the values seem higher than usual
    
    A = None
    
    if A2 not in G.nodes():
        return None
    
    #A2 starts as an Endpoint with same ID but no steps
    #Get the actual endpoint in G to access its steps
    for g in G.nodes():
        if A2 == g:
            A = g
            break
    
    #print("A type: ", type(A))
    if F not in A.steps:
        print("FAIL! no path from A to F")
        
        for k, v in A.steps.items():
            print("     ", k, ": ", v)
        
        return None
    
    #draw_tree(G)
    
    last_A = A
    
   

    while not A == F: #N[F] == 0
    
        print("1. FIND: ", A, " TO ", F)
    
        for N in G.neighbors(A):
            print("     2. TO ", F ," THROUGH ", N, " FROM A: ", A.steps[F])
            
            for f, v in N.steps.items():
                print("         N[", str(f), "]: ", str(v))
            
            if F in N.steps and N.steps[F] == A.steps[F] - 1:
                
                print("     3. USING ", N)
                
                chosen_path = None
                
                if A.start_exit_type == StartExitType.START:
                    chosen_path = choose_path(G, A, N, prioritize_oneway)
                    
                    room_name = chosen_path.room_name
                    if room_name not in G.removed_paths_by_room_and_endpoints:
                        print("     " + str(room_name) + " not in G after exiting choose path!!")
                    else:
                        print("     " + str(room_name) + " in G after exiting choose path!!")
                     
                chosen_endpoints.append((A, chosen_path))
                
                last_A = A
                A = N
                
                break #to next while loop
        
        if A == last_A:
            print("For some reason saw F in A but not in any N of A")
            break
    
    chosen_endpoints.append((F, None)) #If F is START, assume it is being appended to some already existing path choice

    return chosen_endpoints

def choose_path(G, A, F, prioritize_oneway):
    paths_of_types = G.all_paths[(A, F)]
    path = paths_of_types[0]
    
    if prioritize_oneway:
        for p in paths_of_types:
            if p.is_oneway:
                path = p
                break
    
    room_name = path.room_name
    remove_all_room_paths_by_path(G, path)
    
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
def flow(G): 
    #initial seed
    #empty the dicts and set 0 steps to self
    for N in G.nodes():
        N.steps = {}
        N.steps[N] = 0
        N.next_steps = {}

        
    
    GR = G.reverse()
    GR.round = 0
    GR.added_this_round = False
    
    while (True):
        GR.round = GR.round + 1
        #print("Flow round " + str(round))
        
        pass_values_from_all(GR) #flow backwards
        
        GR.added_this_round = False
        
        #finalize all new steps only after
        #all threads in round finished
        #print("add new to all")
        add_new_to_all(GR)

        
        if not GR.added_this_round:
            #print("break not added this round")
            break #end when no new steps flowed back
    
    FG = GR.reverse()
    FG.__dict__.update(G.__dict__) #keep G's attributes in FG
    
    return FG

def add_new_to_all(GR):
    threads = []
        
    #move next steps to steps
    for N in GR.nodes():
        t = threading.Thread(target=add_new, args=(GR, N))
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

def add_new(GR, N):
    curr = N.steps
    next = N.next_steps

    for key, value in next.items():
        if key not in curr:
            curr[key] = value
            GR.added_this_round = True
            #print("     ADDED THIS ROUND")
        #else:
            # print(f"   {N}[{key}] < {value} already there")
    
    N.steps = curr
    N.next_steps = {}

def pass_values(GR, N):
    #print(f"Passing N's steps to reverse neighbors")
    
    for RN in GR.neighbors(N):
        to_add = N.steps
        
        #current round should always match
        #value + 1
        for K in to_add:
            RN.next_steps[K] = GR.round
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
import seeded_random

def grow_path(G, endpoint_path, prioritize_oneway = False):
    
    XZs = []
    i_F = len(endpoint_path) - 1
    
    si_X, si_Z = init_markers(i_F)
    i_X = si_X
    i_Z = si_Z
    
    while (True):
        print("Grow segment " + str(endpoint_path[i_X][0]) + " to " + str(endpoint_path[i_Z][0]))
        print("     i_X, i_Z: " + str(i_X) + ", " + str(i_Z))
        
        X = endpoint_path[i_X][0]
        Y = endpoint_path[i_X + 1][0]
        Z = endpoint_path[i_Z][0]
        
        #temp add removed paths
        #so new path can use P from removed rooms R
        path_XZ = get_endpoint_path_segment(endpoint_path, i_X, i_Z - 1) #include X because it is old XY, exclude Z because it will be kept for ZF
        add_all_room_paths(G, path_XZ) #temp readd old paths from XZ
        
        current_steps_X_to_Z = len(path_XZ)
        N = check_for_new_path(G, X, Y, Z, current_steps_X_to_Z)
        
        if N:
            
            #find separately to force our path down N instead of Y
            path_XN = find_path(G, X, N, prioritize_oneway)
            path_NZ = find_path(G, N, Z, prioritize_oneway)

            path_AX = get_endpoint_path_segment(endpoint_path, 0, i_X - 1) #exclude X because X is part of XN
            path_XN = get_endpoint_path_segment(path_XN, 0, len(path_XN) - 2) #include X, exclude N because N is part of NZ(-2 bc len is + 1)
            path_NZ = get_endpoint_path_segment(path_NZ, 0, len(path_NZ) - 2) #include N, exclude Z because it is part of ZF (-2 bc len is + 1)
            path_ZF = get_endpoint_path_segment(endpoint_path, i_Z, i_F)   #include Z because Z from NZ does not have a room picked
            
            path_AXNZF = reconstruct_endpoint_path_from_segments([path_AX, path_XN, path_NZ, path_ZF])
            
            size_increase = len(endpoint_path) - len(path_AXNZF)
            
            return path_AXNZF, size_increase
        else:
            #re-remove the readded paths since were still using them
            #the readded paths were from path_XZ
            remove_all_endpoint_path_room_paths(G, path_XZ)
            
            i_X, i_Z = increment_exhaustive(si_X, si_Z, i_X, i_Z, i_F)
            
            if i_X == None:
                print("======== FAILED TO GROW")
                return endpoint_path, 0

#Return two values X, Z where 0 <= X < Z <= F
def init_markers(max_F):
    si_X = seeded_random.randint(0, max_F - 1) #A <= X < Z <= F therefore X <= F - 1
    max_Z_offset = max_F - si_X
    si_Z_offset = seeded_random.randint(1, max_Z_offset) # X < X + Z <= F; X + (1) > X; X + (F - X) <= F
    si_Z = si_X + si_Z_offset
    
    return si_X, si_Z

def increment_exhaustive(start_X, start_Z, current_X, current_Z, max_F):
    current_Z_offset = current_Z - current_X #recalculate current offset 
    start_Z_offset = start_Z - start_X #recalculate start offset
    max_Z_offset = max_F - current_X #recalculate max
    
    #Increment Offset
    current_Z_offset = increment_wrap_around(current_Z_offset, 1, max_Z_offset)

    #if Z has finished one cycle then:
    #offset has reached starting offset value OR
    #offset has reached max and max is less than starting offset value

    if current_Z_offset == start_Z_offset or (current_Z_offset == max_Z_offset and max_Z_offset < start_Z_offset ):
        
        #increment to next X
        current_X = increment_wrap_around(current_X, 0, max_F - 1)
        
        #reset offset so every X round starts at the same initial Z
        current_Z_offset = start_Z_offset 
        
        #exhausted all combinations
        if current_X == start_X:
            return None, None
    
    #account for increasing X so that Z = X + offset <= F
    max_Z_offset = max_F - current_X
    
    #clamp in case new X limits max offset
    current_Z_offset = min(current_Z_offset, max_Z_offset)
    
    #Set Z to new X + Offset
    current_Z = current_X + current_Z_offset
    
    return current_X, current_Z

def increment_wrap_around(current, min_inclusive, max_inclusive):
    current = current + 1
    
    if max_inclusive <= min_inclusive:
        return max_inclusive
    
    if current > max_inclusive:
        return min_inclusive
    else:
        return current

def print_path(path):
    print("path: ")
    for S in path:
        print(f"    {str(S[0])} via {str(S[1])} > ")

def check_for_new_path(G, X, Y, Z, current_steps_X_to_Z):
    
    for N in G.neighbors(X):
        if N is not Y and Z in N.steps and N.steps[Z] >= current_steps_X_to_Z:
            print(f"Found path from {str(X)} to {str(Z)} through {str(N)} with steps {N.steps[Z]} >= {current_steps_X_to_Z}")
            
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

#TODO: also check for path types in G that have only one remaining path and hide it
#or unhide it if we readd a path of that type

def remove_all_endpoint_path_room_paths(G, endpoint_path):
    for endpoint_path_pair in endpoint_path:
        path = endpoint_path_pair[1]
        
        if path:
            remove_all_room_paths_by_path(G, path)

def remove_all_room_paths_by_path(G, path):
    room_name = path.room_name
    remove_all_room_paths_by_room(room_name, G)

def remove_all_room_paths_by_room(room_name, G):
    if room_name in G.removed_rooms: #if already removed dont re-remove
        return
    
    G.removed_any_edge = False
    G.removed_paths = []
    
    threads = []
    
    G.removed_rooms.append(room_name) #keep track of rooms not in G
    
    if room_name in G.readded_rooms:  #keep readded updated with rooms immediately removed after readd (such as by hide)
        G.readded_rooms.remove(room_name)
    
    for endpoint_pair, paths in G.all_paths.items():
        t = threading.Thread(target=remove_room_paths, args=(endpoint_pair, room_name, paths, G))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    if G.removed_any_edge or G.added_any_edge:
        G = flow(G)
    
    G.removed_paths_by_room_and_endpoints[room_name] = {}
    
    #Store removed paths by room then by endpoint
    for endpoint_pair_and_path in G.removed_paths:
        
        endpoint_pair = endpoint_pair_and_path[0]
        path = endpoint_pair_and_path[1]
        
        if endpoint_pair not in G.removed_paths_by_room_and_endpoints[room_name]:
            G.removed_paths_by_room_and_endpoints[room_name][endpoint_pair] = [path]
        else:
            G.removed_paths_by_room_and_endpoints[room_name][endpoint_pair].append(path)

#remove all paths of type that are from the specificed room
def remove_room_paths(endpoint_pair, room_name, paths, G):
    new_paths = []
    
    original_length = len(paths)
    
    for P in paths:
        if not P.room_name == room_name:
            new_paths.append(P)
        else:
            #store removed path as its endpoint pair and the path
            G.removed_paths.append((endpoint_pair, P))
    
    G.all_paths[endpoint_pair] = new_paths
    
    #Dont remove edge if already removed, maybe could check original length instead? 
    #This can happen if the original size of paths was 0
    if len(new_paths) == 0 and not original_length == 0 : 
        G.remove_edge(endpoint_pair[0], endpoint_pair[1])
        G.removed_any_edge = True
    
    #if len == 1, do a hide for that path's room
    elif len(new_paths) == 1 and not original_length == 1:
        G.remove_edge(endpoint_pair[0], endpoint_pair[1])
        G.removed_any_edge = True
        
        hide_room_by_path(G, new_paths[0]) #calls remove rooms so each removed room will cascade hide to any other rooms caused by hiding the initial room
    
    

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


def add_all_room_paths(G, endpoint_path):
    G.added_any_edge = False
    threads = []
    used_room_names = []
    
    for endpoint_and_path in endpoint_path:
        
        path = endpoint_and_path[1]

        #if the endpoint has an associated RoomPath
        if path: 
            room_name = path.room_name
            
            if room_name not in used_room_names and room_name in G.removed_rooms: #prevent multiple threads for the same room from being created
                used_room_names.append(room_name)
                
                G.removed_rooms.remove(room_name)
                
                t = threading.Thread(target=add_room_paths, args=(room_name, G))
                threads.append(t)
                t.start()
    
    for t in threads:
        t.join()
    
    if G.added_any_edge or G.removed_any_edge:
        G = flow(G)

def add_room_paths(room_name, G):
    print("     " + str(room_name) + " marked to readd")

    if room_name in G.removed_paths_by_room_and_endpoints:
        G.readded_rooms.append(room_name) #keep track of rooms readded to G

        #for updating other Gs
        if room_name in G.removed_rooms:
             G.removed_rooms.remove(room_name)

        removed_paths_by_endpoint = G.removed_paths_by_room_and_endpoints[room_name]
        
        for endpoint_pair, paths in removed_paths_by_endpoint.items():
            
            original_length = len(G.all_paths[endpoint_pair])
            G.all_paths[endpoint_pair].extend(paths)
            
            if (original_length == 0):
                G.add_edge(endpoint_pair[0], endpoint_pair[1])
                G.added_any_edge = True
                
                #check if unhiding any room would result only in endpoint paths > 1
                check_if_any_room_should_unhide(G, endpoint_pair)
                
                #if length is still one, hide it
                if len(G.all_paths[endpoint_pair]) == 1:
                    hide_room_by_path(G, G.all_paths[endpoint_pair][0])
            
            
        
        del G.removed_paths_by_room_and_endpoints[room_name]
    else:
        print("     " + str(room_name) + " not in G")

#Update all other G to remove/readd rooms removed/readded in G
def update_other_G(G, others):
    
    to_readd = G.readded_rooms
    to_remove = G.removed_rooms 
    to_hide = G.hidden_rooms
    
    
    #readd all to readd that's in O.removed
    for O in others:
        
        for room in to_readd:
            print("O to readd ", room)
            
            if room in O.removed_rooms or room in O.hidden_rooms:
                print("     O do readd ", room)
                add_room_paths(room, O)
    
    #hide all in to hide
    for O in others:
    
        for room in to_hide:
            print("O to hide ", room)
            
            if room not in O.hidden_rooms:
                print("     do hide ", room)
                hide_room_by_room(O, room)
            else:
                print("     ", room, " already hidden? ")
    
    #remove all in to remove
    for O in others:
        
        for room in to_remove:
            print("O to remove ", room)
            if room not in O.removed_rooms and room not in O.hidden_rooms:
                print("     do remove ", room)
                remove_all_room_paths_by_room(room, O)
            else:
                print("     ", room, " already removed? ")
    
   
    
    
    #reflow
    for O in others:
        if O.added_any_edge or O.removed_any_edge:
            O = flow(O)
    
    print("===G UPDATE===")
    
    for a in to_readd:
        print("     readded: ", a)
    
    for r in to_remove:
        print("     removed: ", r)
    
    for h in to_hide:
        print("     hidden: ", h)
    
    for O in others:
        print("===O UPDATE===")
    
        for a in O.readded_rooms:
            print("     readded: ", a)
        
        for r in O.removed_rooms:
            print("     removed: ", r)
        
        for h in O.hidden_rooms:
            print("     hidden: ", h)
    
    G.readded_rooms = [] #clear because we dont need to know which were readded anymore

def unhide_rooms(G, rooms):
    return #TODO: debug, dont do anything
    
    for room in rooms:
        print("try unhide ", room_name)
        
        if room in G.hidden_rooms:
            print("     do unhide by readd ", room_name)
            G.hidden_rooms.remove(room)
            add_room_paths(room, G)
    
    if G.added_any_edge or G.removed_any_edge:
        G = flow(G)

def hide_room_by_path(G, path):
    room_name = path.room_name
    hide_room_by_room(G, room_name)
    

def hide_room_by_room(G, room_name):
    return #TODO: debug, dont do anything
    
    if room_name not in G.hidden_rooms:
        G.hidden_rooms.append(room_name)
        remove_all_room_paths_by_room(room_name, G)
        
        if room_name in G.removed_rooms:        #dont want to store hidden rooms in removed rooms array
            print("     remove room from removed room after hide")
            for r in G.removed_rooms:
                print("         before removed: ", r)
            
            G.removed_rooms.remove(room_name)
        else:
            print("     room not in removed after hide")
        
            for r in G.removed_rooms:
                print("         in removed: ", r)

def check_if_any_room_should_unhide(G, endpoint_pair):
    
    to_unhide = []
    
    for room_name in G.removed_paths_by_room_and_endpoints:
        
        if room_name in G.hidden_rooms:
            removed_paths_by_endpoints = G.removed_paths_by_room_and_endpoints[room_name]
            
            if endpoint_pair in removed_paths_by_endpoints:
                
                should_unhide = True
                
                for other_pair in removed_paths_by_endpoints:
                    
                    future_length = len(removed_paths_by_endpoints[other_pair]) + len(G.all_paths[other_pair])
                    
                    #if any endpoint type readded would not end up with more than one path, do not unhide the room at all
                    if not future_length > 1:
                        should_unhide = False
                        break
                
                if should_unhide:
                    to_unhide.append(room_name)
    
    unhide_rooms(G, to_unhide)
                    
    