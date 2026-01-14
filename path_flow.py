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


TODO: implement
Additionally, the parent also prioritizes a step count with fewer hidden
steps, even if the total step count is higher. This ensures that the fewest
hidden steps are used when using any path A to F

#reflow_with_hidden_steps(G, max_hidden_steps) (flow up)
#       for each node N: (flow N to P)
#           for each parent P of N:
#               store N.hidden_steps[F][steps] + 1 in P.next_hidden_steps[F][N][steps]
#               store N.hidden_steps[F][hidden steps] + (1 or 0 depending on edge) to P.next_hidden_steps[F][N][hidden steps]
#       
#       for each node P: (add new for P)
#           for each value in P.next_hidden_steps[F]
#               get the nhs[F][N]'s with the smallest hidden steps values 
#               IMPORTANT: include CURRENT steps and hidden steps, since that might be the samllest number of hidden steps/steps combo arleady
#               of those, get the nhs[F][N] with the smallest steps
#               set P.hidden_steps[F][steps] to smallest steps
#               set P.hidden_steps[F][hidden steps] to smallest hidedn steps value
"""

import threading

def reflow(G):
    if G.updated_since_last_flow:
        print("Did reflow")
        return flow(G)
    
    print("did NOT reflow because it was not updated since last flow")
    return G

def print_flow(G):
    for N in G.nodes():
        print("     ", N)
        
        for k, v in N.steps.items():
            print("         ", k, ": ", v)

def flow(G): 
    G.updated_since_last_flow = False
    
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
        
        pass_values_from_all(GR) #flow backwards
        
        GR.added_this_round = False
        
        #finalize all new steps only after
        #all threads in round finished
        add_new_to_all(GR)

        if not GR.added_this_round:
            break #end when no new steps flowed back
    
    FG = GR.reverse()
    FG.__dict__.update(G.__dict__) #keep G's attributes in FG
    
    #print_flow(FG)
    
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
            
            
    
    N.steps = curr
    N.next_steps = {}

def pass_values(GR, N):
    for RN in GR.neighbors(N):
        to_add = N.steps
        
        #current round should always match
        #value + 1
        for K, _ in to_add.items():
            RN.next_steps[K] = GR.round