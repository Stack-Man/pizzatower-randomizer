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


We have to ask two things:
Can this algo loop paths?
Can this algo destroy assumed paths?

Assumptions:
1. In any round R, the number of total steps ebing passed back is R
2. In any round R, the number of hidden steps being passed back is <= R

Can loop?

Any loop is the same as some unlooped path excluding the repeated segment except longer
This means total steps is larger and hidden steps is either larger or same

If hidden same, no, because steps is larger
If hidden not same, its larger, no because hidden is larger
therefore, cannot loop

Can destroy paths?

Assume A has some path to F from B
for B's path to F to change, the number of hidden or total steps must be less
the number of total steps can NOT be less

therefoer, the number of hidden steps must be less
the number of hidden steps COULD be less if some path of length R reaches B and has less hidden steps to F then the n current B[F]
this path to F would then be passed back from B to A in the next round and replace its old path because the nubmer of hidden steps is less than what 
B passed to A before

What is the stopping point?
before we would stop if no node got a shorter path
now we stop if no node gets a shorter path and no node gets a path with less hidden steps

if no node receives a new path, then no node needs to alert any of its parents of new nodes
therefore, we can stop

we also stop after N rounds where N is number of nodes
because the longest path is through N nodes
if its longer than N nodes, it must have gone through every node once
and at least one node more than once
if we repeated a visit to a node, we could have gone from that node to the shorter path earlier than we did
because that path necessairly has less total steps and possibly less hidden steps
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
    
    while (True):
        GR.round = GR.round + 1
        
        pass_steps_and_hidden_from_all(GR) #flow backwards
        
        GR.added_this_round = False
        
        add_shortest_fewest_hidden_path_to_all(GR) #confirm which passed are kept
        
        if not GR.added_this_round: #all shortest paths finished
            break
    
    FG = GR.reverse()
    FG.__dict__.update(G.__dict__) #keep G's attributes in FG
    
    return FG

def flow(G): 
    return flow_fewest_hidden_steps(G) #TODO: override with new method, test if works
    
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
    
    GR.__dict__.update(G.__dict__) #Add G's attributes to GR to know hidden edges
    
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

#       for each node N: (flow N to P)
#           for each parent P of N:
#               store N.hidden_steps[F][steps] + 1 in P.next_hidden_steps[F][N][steps]
#               store N.hidden_steps[F][hidden steps] + (1 or 0 depending on edge) to P.next_hidden_steps[F][N][hidden steps]

def pass_steps_and_hidden_from_all(GR):
    threasd = []
    
    for N in GR.nodes():
        t = threading.Thread(target = pass_steps_and_hidden, args=(GR, N))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

def pass_steps_and_hidden(GR, N):
    to_pass = N.steps
    
    for P in GR.neighbors(N):
        
        edge_is_hidden = (P, N) in GR.hidden_edges #TODO: mark edges as hidden instead of removing them
        
        for F, steps in to_pass.items():
            
            new_steps = steps.steps + 1
            new_hidden_steps = steps.hidden_steps
            
            if edge_is_hidden:
                new_hidden_steps = new_hidden_steps + 1
            
            steps_passed_to_P_from_N = Steps(new_steps, new_hidden_steps)
            
            RN.next_steps[F][N] = steps_passed_to_P_from_N

#       for each node P: (add new for P)
#           for each value in P.next_hidden_steps[F]
#               get the nhs[F][N]'s with the smallest hidden steps values 
#               IMPORTANT: include CURRENT steps and hidden steps, since that might be the samllest number of hidden steps/steps combo arleady
#               of those, get the nhs[F][N] with the smallest steps
#               set P.hidden_steps[F][steps] to smallest steps
#               set P.hidden_steps[F][hidden steps] to smallest hidedn steps value
def add_shortest_fewest_hidden_path_to_all(GR):
    threads = []
        
    #move next steps to steps
    for N in GR.nodes():
        t = threading.Thread(target=add_shortest_fewest_hidden_path, args=(GR, N))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

def add_shortest_fewest_hidden_path(GR, P):
    curr = P.steps
    next = P.next_steps

    for F, candidate_Ns in next.items(): #for every F sent to P this round
        
        if F not in P.steps:
            P.steps[F] = Steps(None, None)
        
        fewest_hidden = P.steps[F].hidden_steps
        fewest_total_steps = P.steps[F].steps
        
        for N, N_steps in candidate_Ns.items(): #for every N that sent this F
            
            current_hidden = N_steps.hidden_steps
            current_total_steps = N_steps.steps
            
            #if this N has less hidden steps, use it
            #if None, initialize with this N instead of P
            if fewest_hidden = None or current_hidden < fewest_hidden:
                fewest_hidden = current_hidden
                fewest_total_steps = current_total_steps
            #if this N has same hidden steps but less total steps, use it
            elif current_hidden = fewest_hidden and current_total_steps < fewest_total_steps: 
                fewest_total_steps = current_total-steps
    
        #finalize the steps to F in P
        P.steps[F].hidden_steps = fewest_hidden
        P.steps[F].steps = fewest_total_steps

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