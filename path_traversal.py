import networkx as nx
from node_id_objects import StartExitType
from copy import deepcopy
import path_graph, path_flow

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

def sync_base_room_lists(to_remove, others):
    
    for O in others:
        if to_remove in O:
            O.remove(to_remove)

def create_bridge_twoway(G, As, Fs, to_sync_G = [], to_sync_A = [], to_sync_F = []): #As and Fs should be lists of types inheriting BaseRoom
    
    print("Try Bridge Twoway")
    
    def twoway_endpoint_extractor(A):
        return A.get_twoway_endpoint()

    chosen_A, chosen_F, twoway_path_AF = find_some_path_with_unhides(G, As, Fs, endpoint_extractor = twoway_endpoint_extractor, prioritize_oneway = False)
    
    path_graph.update_other_G(G, to_sync_G)
    
    sync_base_room_lists(chosen_A, to_sync_A)
    sync_base_room_lists(chosen_F, to_sync_F)
    
    return chosen_A, chosen_F, twoway_path_AF

def create_bridge_oneway(G_NPT, G_PT, BSs, BEs, to_sync_G = [], to_sync_BS = [], to_sync_BE = []): #BSs and #BEs should be lists of type BranchRoom
    
    print("Try Bridge Oneway")
    
    chosen_BS, chosen_BE, oneway_path_NPT, oneway_path_PT = find_some_branch_paths_with_unhides(G_PT, G_NPT, BSs, BEs)
    
    path_graph.update_other_G(G_NPT, to_sync_G)
    path_graph.update_other_G(G_PT, to_sync_G) #TODO: unnecessary because PT is updated by NPT?

    sync_base_room_lists(chosen_BS, to_sync_BS)
    sync_base_room_lists(chosen_BE, to_sync_BE)
    
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
    
    max_unhidden_rooms_at_once = len(G.hidden_rooms)
    room_count_to_unhide_this_round = 0
    
    while (room_count_to_unhide_this_round <= max_unhidden_rooms_at_once):
        
        #try to find a path with every unique combination of hidden rooms unhidden
        #when successful, replace G with that created G
        
        #TODO TODO:
        #Refactor flow and find to always account for hidden steps
        #node A should store the step count to F that is firstly, the fewest hidden steps
        #and amongst all with fewest hidden steps, then the fewest total steps
        #
        #1. redo hiding, still need to hide rooms because we want to remove all paths of that room so they arent chosen by chose_path for a DIFFERENT edge
        #   than the edge that room is being hidden for, but the current hiding does too much i thnk
        #2. make new algo with flow, count hidden edges and use fewest hidden steps prioritized then fewest total steps
        #2. make new algo for find that follows the number of hidden edges in addition to following the number of steps
        #3. remove room combo choose algo, instead just unhide and go
        
        
        
        for room_combination in choose(G.hidden_rooms, room_count_to_unhide_this_round): #TODO: RUNS EXPONENTIALLY
            
            temp_G = path_graph.temp_unhide_rooms(G, room_combination)

            chosen_A, chosen_F, path_AF = find_some_path(temp_G, As, Fs, endpoint_extractor, prioritize_oneway)
            
            if path_AF is not None:
                G = temp_G
                return chosen_A, chosen_F, path_AF
        
        room_count_to_unhide_this_round = room_count_to_unhide_this_round + 1 #try next round with more unhidden rooms
    
    #failed
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
def find_some_branch_paths_with_unhides(G_PT, G_NPT, BSs, BEs): #TODO: stuck in an infinite loop checking for "1. START AT START DOOR NONE", or maybe just too many prints to go quickly?
    #Assum As and Fs are lists of BranchRoom
    
    max_unhidden_rooms_at_once = len(G_NPT.hidden_rooms)
    room_count_to_unhide_this_round = 0
    
    def branch_extractor_NPT(A):
        return A.NPT_endpoint
    
    def branch_extractor_PT(A):
        return A.PT_endpoint
    
    while (room_count_to_unhide_this_round <= max_unhidden_rooms_at_once):
        
        #try to find a path with every unique combination of hidden rooms unhidden
        #when successful, replace G with that created G

        for room_combination in choose(G_NPT.hidden_rooms, room_count_to_unhide_this_round): #TODO: RUNS EXPONENTIALLY
            
            #First try to find NPT
            #print("temp unhide NPT from some path branch with unhides")
            temp_G_NPT = path_graph.temp_unhide_rooms(G_NPT, room_combination)
            chosen_BS, chosen_BE, path_NPT = find_some_path(temp_G_NPT, BSs, BEs, endpoint_extractor = branch_extractor_NPT, prioritize_oneway = True)
            
            #Then try to find PT with this NPT
            if path_NPT is not None:
                
                #unhide the rooms unhidden by this successful NPT
                temp_G_PT = path_graph.temp_unhide_rooms(G_PT, room_combination) 
                
                #update removed/readded from successful NPT
                path_graph.update_other_G(temp_G_NPT, [temp_G_PT])
            
                #try find path with unhides, uses a G, F, and A  based on the current NPT
                _, _, path_PT = find_some_path_with_unhides(temp_G_PT, [chosen_BE], [chosen_BS], endpoint_extractor = branch_extractor_PT, prioritize_oneway = True)
                
                if path_PT is not None: #successful, replace Gs and exit
                    G_PT = temp_G_PT
                    G_NPT = temp_G_NPT
                    
                    return chosen_BS, chosen_BE, path_NPT, path_PT
    
        room_count_to_unhide_this_round = room_count_to_unhide_this_round + 1 #try next round with more unhidden rooms
    
    print("Failed to bridge oneway")
    return None, None, None, None

#yield every unordered combo of items
def choose(items, k):
    
    if k <= 0:
        yield []
    elif k == 1:
        for i in items:
            yield [i]
    else:
        for x, i in enumerate(items):
            
            items_after_i = items[x+1:]
            
            for rest in choose(items_after_i, k - 1):
                
                rest_with_i = rest.copy()
                rest_with_i.append(i)
                
                yield rest_with_i

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

    for Au in As:
        
        if Au is None:
            print("None in As?")
            continue
        
        A = endpoint_extractor(Au)
         
        for Fu in Fs:
        
            F = endpoint_extractor(Fu)
            path_AF = find_path(G, A, F, prioritize_oneway)
            
            if path_AF is not None:
                return Au, Fu, path_AF
    
    #Exhausted all AF combos in G
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

#TODO: implement considering number of hidden steps required
#find_path_with_hidden_steps (flow down)
#    A = start
#   for each neighbor N to A
#       if N.hidden_steps[F][steps] = A.hidden_steps[F][steps] - 1
#       AND if N.hidden_steps[F][hidden steps] = A.hidden_steps[F][hidden steps] - (1 or 0 depending on edge):
#       A = N
#   repeat

#RETURN: List of (Endpoint, Path) for every chosen Endpoint and their 
#related path EXIT endpoints have Path set as None
def find_path(G, A2, F, prioritize_oneway = False):
    chosen_endpoints = []
    
    A = None
    
    #used to allow temp removal of bad endpoints (ones that cannot reach F without breaking the path)
    #while preserving the original graph if necessary
    temp_G = path_graph.copy_graph(G) 
    
    if A2 not in temp_G.nodes():
        raise RuntimeError("A not found in G")
    
    #A2 starts as an Endpoint with same ID but no steps
    #Get the actual endpoint in G to access its steps
    for g in temp_G.nodes():
        if A2 == g:
            A = g
            break
    
    if F not in A.steps:
        return None
    
    while not A == F:
    
        temp_G = path_flow.reflow(temp_G) #reflow before accessing steps
    
        if F not in A.steps:
            raise RuntimeError("A no longer contains F!")
    
        print("1. START AT ", str(A), " TO ", str(F), " IN ", A.steps[F])
        
        last_A = A
    
        for N in temp_G.neighbors(A):
            
            print("     1a. Try N ", str(N))
            
            if F in N.steps and N.steps[F] == A.steps[F] - 1:
                
                print("     2. THROUGH ", str(N), " IN ", N.steps[F])
                
                chosen_path = None
                
                if A.start_exit_type == StartExitType.START:
                    chosen_path = choose_path(temp_G, A, N, F, prioritize_oneway) 
                    if chosen_path is None:
                        print("             3. Failed to find path AN that doesnt disrupt NF")

                        continue
                     
                chosen_endpoints.append((A, chosen_path))
                
                print("         2a. MADE IT THROUGH ", str(N), " IN ", N.steps[F])
                A = N
                
                break #exit neighbor loop
        
        if not last_A == A: #A advanced to N
            continue #skip to next while loop
        
        #else exhausted all N
        #This means that A is a bad node in the graph
        
        #1. set bad_A to A
        #2. set A to prev_A #if empty, we failed to find AF
        #3. refund prev_A to A if not None
        #4. temp remove bad A from G
        
        if len(chosen_endpoints) == 0:
            print("Failed find_path, No good A to F")
            return None
        
        print("         4. No good N from A, backtrack")
        
        prev_A, to_refund = chosen_endpoints.pop() 

        if to_refund is not None:
            path_graph.add_rooms_by_endpoint_path(temp_G, [(prev_A, to_refund)])
        
        bad_A = A
        path_graph.remove_endpoint(temp_G, bad_A)
        
        A = prev_A #continue from previous A
    
    chosen_endpoints.append((F, None)) #If F is START, assume it is being appended to some already existing path choice
    
    #TODO: take chosen paths and remove them from G
    path_graph.remove_rooms_by_endpoint_path(G, chosen_endpoints)

    return chosen_endpoints


def choose_path(G, A, N, F, prioritize_oneway):
    paths_of_types = G.all_paths[(A, N)]
    
    if len(paths_of_types) == 0:
        raise RuntimeError("Tried to choose path of ", str(A), " to ", str(F), " but there are none left!")
    
    #TODO TODO: check room of chosen path
    #see if room is supposed to be hidden
    #prioritize non-hidden room paths if possible
    #basically, set path as the hidden path
    #and keep going and if we dont find any non-hidden path well use it
    #how to interact with oneway?
    #prefer unhidden over hidden oneway i think
    chosen_path = None
    
    for p in paths_of_types:
        
        temp_G = path_graph.temp_remove_room_by_path(G, p)
        temp_N = None
        
        for t in temp_G.nodes():
            if t == N:
                temp_N = t
                break
        
        temp_G = path_flow.reflow(temp_G) #must reflow before we access steps
        
        removal_disrupts_path = F not in temp_N.steps 
        
        print("Try path p of ", len(paths_of_types),  "removal bad? ", removal_disrupts_path)
        
        #N to F should be intact ,the path we should was A to N
        #but removal of the room of p might disrupt N to F
        #and therefore p cannot be used
        
        if not removal_disrupts_path:
            
            if prioritize_oneway and p.is_oneway: #break if want and found oneway
                chosen_path = p
                break
            else: #continue until oneway is found or exhaused all p
                chosen_path = p
            
            if not prioritize_oneway: #break if not want oneway and found path
                chosen_path = p
                break
    
    if chosen_path is not None:
        path_graph.remove_room_by_path(G, chosen_path)
    
    return chosen_path

def find_longer_path_first_step(G, X, Y, Z, current_steps_X_to_Z):
    #reflow before accessing .steps
    G = path_flow.reflow(G)
    
    for N in G.neighbors(X):
        if N is not Y and Z in N.steps and N.steps[Z] >= current_steps_X_to_Z:
            print(f"Found path from {str(X)} to {str(Z)} through {str(N)} with steps {N.steps[Z]} >= {current_steps_X_to_Z}")
            
            return N
    
    return None

    