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
        for room_combination in choose(G.hidden_rooms, room_count_to_unhide_this_round):
            
            temp_G = path_graph.temp_unhide_rooms(G, room_combination)

            chosen_A, chosen_F, path_AF = find_some_path(temp_G, As, Fs, endpoint_extractor, prioritize_oneway)
            
            if path_AF is not None:
                G = temp_G
                return chosen_A, chosen_F, path_AF
        
        room_count_to_unhide_this_round = room_count_to_unhide_this_round + 1 #try next round with more unhidden rooms
    
    #failed
    print("failed to find some path")
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
        for room_combination in choose(G_NPT.hidden_rooms, room_count_to_unhide_this_round):
            
            #First try to find NPT
            temp_G_NPT = path_graph.temp_unhide_rooms(G_NPT, room_combination)
            chosen_BS, chosen_BE, path_NPT = find_some_path(temp_G_NPT, BSs, BEs, endpoint_extractor = branch_extractor_NPT, prioritize_oneway = True)
            
            #Then try to find PT with this NPT
            if path_NPT is not None:
                
                #unhide the rooms unhidden by this successful NPT
                temp_G_PT = path_graph.temp_unhide_rooms(G_PT, room_combination) 
                
                #update removed/readded from successful NPT
                path_graph.update_other_G(temp_G_NPT, [temp_G_PT])
            
                #try find path with unhides, uses a G, F, and A  based on the current NPT
                
                
                #-------------------------------
                #TODO: FAILS CURRENTLY, might not fail anymore after fixing deepcopy, except the fact it loops forever
                #-------------------------------
                _, _, path_PT = find_some_path_with_unhides(temp_G_PT, [chosen_BE], [chosen_BS], endpoint_extractor = branch_extractor_PT, prioritize_oneway = True)
                
                if path_PT is not None: #successful, replace Gs and exit
                    G_PT = temp_G_PT
                    G_NPT = temp_G_NPT
                    
                    return chosen_BS, chosen_BE, path_NPT, path_PT
                else:
                    print("Failed to bridge oneway PT with this NPT")
            else:
                print("Failed to bridge oneway NPT with this combo")
    
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
#RETURN: List of (Endpoint, Path) for every chosen Endpoint and their 
#related path EXIT endpoints have Path set as None
def find_path(G, A2, F, prioritize_oneway = False):
    chosen_endpoints = []
    
    A = None
    
    if A2 not in G.nodes():
        return None
    
    #A2 starts as an Endpoint with same ID but no steps
    #Get the actual endpoint in G to access its steps
    for g in G.nodes():
        if A2 == g:
            A = g
            break
    
    if F not in A.steps:
        return None
    
    last_A = A
    
    print("G FLOW FROM find_path")
    
    for N in G.nodes():
        #print("     SELF: ", N, " TO SELF: ", N.steps[N])
        for k, v in N.steps.items():
            print("     KEY: ", N, " TO ", k, ": ", v)
    
    while not A == F:
    
        #-------------------------------
        #TODO: Forced to flow despite G.has_updated_since_last_flow = false
        #Without it, values are inaccurate and also nonsensical
        #such as steps to self being > 0
        #The only time steps are set is in flow, right?
        #therefore, the issue must be there
        #maybe something like because im not resetting all steps values
        #before doing the flow, some carry over occurs, causing a mess
        #the values also seem strangely high sometimes but im not sure
        #
        #not so, we do empty steps before we begin the flow
        #-------------------------------
        #G = path_flow.flow(G) #reflow before accessing steps
        G = path_flow.reflow(G) #reflow before accessing steps
    
        print("1. START AT ", str(A))
        print("2. TO ", str(F), " IN ", A.steps[F])
    
        for N in G.neighbors(A):
            
            print("     3. CHECK ", str(N), " OF ", G.out_degree(A))
            
            for k, v in N.steps.items():
                print("         4. TO ", str(k), " IN ", v)
                
                if k == F:
                    print("             5. WANTED F")
                
                    if v != A.steps[F] - 1:
                        print("                 6. BAD STEPS")
            
            if F in N.steps and N.steps[F] == A.steps[F] - 1:
                
                chosen_path = None
                
                if A.start_exit_type == StartExitType.START:
                    chosen_path = choose_path(G, A, N, prioritize_oneway)
                    print("Chose path " + chosen_path + "should reflow before next check")
                    
                     
                chosen_endpoints.append((A, chosen_path))
                
                last_A = A
                A = N
                
                break #to next while loop
        
        if A == last_A:
            
            """
            print("G's FLOW RIGHT BEFORE ERROR:")
    
            for N in G.nodes():
                
                print("     ", N,"'s STEPS:")
                
                for k, v in N.steps.items():
                    print("         ", k, ": ", v)"""
            
            raise RuntimeError(f"Tried to reach F: {str(F)} from A: {str(A)} that had no neighbors A[F] - 1: {A.steps[F] - 1} steps away from F")
            
            
            
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
    path_graph.remove_room_by_path(G, path)
    
    return path

def find_longer_path_first_step(G, X, Y, Z, current_steps_X_to_Z):
    #reflow before accessing .steps
    G = path_flow.reflow(G)
    
    for N in G.neighbors(X):
        if N is not Y and Z in N.steps and N.steps[Z] >= current_steps_X_to_Z:
            print(f"Found path from {str(X)} to {str(Z)} through {str(N)} with steps {N.steps[Z]} >= {current_steps_X_to_Z}")
            
            return N
    
    return None

    