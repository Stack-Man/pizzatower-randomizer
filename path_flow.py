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


The idea behind this algorithm is that, in each round,
each node N alerts its parents P of all Fs that N can reach
and the number of total steps and hidden steps required to get
there.

Then each parent sees all of the step counts to F from its children
and stores the shortest one it was given (or already has)

backtracking then is a node N looking at each child C for one that
has one less step to F than N does, and either 1 less or same hidden steps,
depending on whether edge NC is hidden or not
"""

import threading

def reflow(G):
    if G.updated_since_last_flow:
        return flow(G)

    return G


def print_flow(G):
    for N in G.nodes():
        print("     ", N)
        
        for k, v in N.steps.items():
            print("         ", k, ": ", v)

from path_objects import Steps

#This flow prioritizes paths with fewer hidden steps over shorter paths
def flow_fewest_hidden_steps(G):
    G.updated_since_last_flow = False
    
    #initial seed
    #empty the dicts and set 0 steps to self
    for N in G.nodes():
        N.steps = {}
        N.steps[N] = Steps(0, 0)
        N.next_steps = {}
    
    GR = G.reverse()
    GR.round = 0
    GR.added_this_round = False
    
    
    #Add G's attributes to GR to know hidden edges
    GR.__dict__.update(G.__dict__) 
    
    print_flow(GR)

    
    while (True):
        GR.round = GR.round + 1
        
        print("     ROUND ", GR.round)
        
        pass_steps_and_hidden_from_all(GR) #flow backwards
        
        GR.added_this_round = False
        
        add_shortest_fewest_hidden_path_to_all(GR) #confirm which passed are kept
        
        #DEBUG: print current flow state
        print_flow(GR)
        
        if not GR.added_this_round: #all shortest paths finished
            break
    
    FG = GR.reverse()
    #keep G's attributes in FG
    FG.__dict__.update(G.__dict__) 
    
    return FG

from node_id_objects import StartExitType

def print_flow(GR):
    print("     ROUND ", GR.round, " FLOW STATE:")
    for N in GR.nodes():
        if N.start_exit_type == StartExitType.START:
            continue
        
        print("         N: ", str(N))
        
            
        for F, steps in N.steps.items():
            
            print("             F: ", str(F), " step: ", steps.steps, " hid: ", steps.hidden_steps)

def flow(G): 
    return flow_fewest_hidden_steps(G)


#       for each node N: (flow N to P)
#           for each parent P of N:
#               store N.hidden_steps[F][steps] + 1 in P.next_hidden_steps[F][N][steps]
#               store N.hidden_steps[F][hidden steps] + (1 or 0 depending on edge) to P.next_hidden_steps[F][N][hidden steps]

def pass_steps_and_hidden_from_all(GR):
    threads = []
    
    print("         PASS FROM ALL")
    
    for N in GR.nodes():
        t = threading.Thread(target = pass_steps_and_hidden, args=(GR, N))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

def pass_steps_and_hidden(GR, N):

    #print("            PASS FROM N: ", str(N))

    for P in GR.neighbors(N):
        
        edge_is_hidden = (P, N) in GR.hidden_edges
        
        for F, steps in N.steps.items():
            
            new_steps = steps.steps + 1
            new_hidden_steps = steps.hidden_steps
            
            if edge_is_hidden:
                new_hidden_steps = new_hidden_steps + 1
            
            steps_passed_to_P_from_N = Steps(new_steps, new_hidden_steps)
            
            if F not in P.next_steps:
                P.next_steps[F] = {}
            
            P.next_steps[F][N] = steps_passed_to_P_from_N
            #print("                 PASS [F]: TO ", str(F), " steps: ", steps_passed_to_P_from_N.steps, " hid: ", steps_passed_to_P_from_N.hidden_steps)

#       for each node P: (add new for P)
#           for each value in P.next_hidden_steps[F]
#               get the nhs[F][N]'s with the smallest hidden steps values 
#               IMPORTANT: include CURRENT steps and hidden steps, since that might be the samllest number of hidden steps/steps combo arleady
#               of those, get the nhs[F][N] with the smallest steps
#               set P.hidden_steps[F][steps] to smallest steps
#               set P.hidden_steps[F][hidden steps] to smallest hidedn steps value
def add_shortest_fewest_hidden_path_to_all(GR):
    threads = []
    
    print("         ADD TO ALL")
    
    #move next steps to steps
    for N in GR.nodes():
        t = threading.Thread(target=add_shortest_fewest_hidden_path, args=(GR, N))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

def add_shortest_fewest_hidden_path(GR, P):
    
    #print("             ADD TO P:", str(P))
    
    for F, candidate_Ns in P.next_steps.items(): #for every F sent to P this round
        
        added_this_F = False
        
        if F not in P.steps:
            P.steps[F] = Steps(None, None)
            
        
        fewest_hidden = P.steps[F].hidden_steps
        fewest_total_steps = P.steps[F].steps
        
        for N, N_steps in candidate_Ns.items(): #for every N that sent this F
            
            current_hidden = N_steps.hidden_steps
            current_total_steps = N_steps.steps
            
            #if this N has less hidden steps, use it
            #if None, initialize with this N instead of P
            if fewest_hidden == None or current_hidden < fewest_hidden:
                fewest_hidden = current_hidden
                fewest_total_steps = current_total_steps
                added_this_F = True
            #if this N has same hidden steps but less total steps, use it
            elif current_hidden == fewest_hidden and current_total_steps < fewest_total_steps: 
                fewest_total_steps = current_total_steps
                added_this_F = True
    
        #finalize the steps to F in P
        P.steps[F].hidden_steps = fewest_hidden
        P.steps[F].steps = fewest_total_steps
    
        if P.steps[F].steps == None: #no replacement for a None, that cant happen or wed never try this F in the first place
            raise RuntimeError("Tried to add F to P.steps that had no valid replacement?")
    
        if added_this_F: #if any F was modified
            GR.added_this_round = True #let outer func know to continue flow