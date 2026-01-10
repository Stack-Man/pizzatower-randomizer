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
import path_traversal

def grow_path(G, endpoint_path, prioritize_oneway = False):
    
    XZs = []
    i_F = len(endpoint_path) - 1
    
    #Locate random segment XZ to grow via replacement
    si_X, si_Z = init_markers(i_F)
    i_X = si_X
    i_Z = si_Z
    
    while (True):
        X = endpoint_path[i_X][0]
        Y = endpoint_path[i_X + 1][0] #Y = original XZ path direction
        Z = endpoint_path[i_Z][0]
        
        #temp add removed paths
        #so new path can use P from removed rooms R
        path_XZ = get_endpoint_path_segment(endpoint_path, i_X, i_Z - 1) #include X because it is old XY, exclude Z because it will be kept for ZF
        add_all_room_paths(G, path_XZ) #temp readd old paths from XZ
        
        #Find replacement N for Y with more steps to Z
        current_steps_X_to_Z = len(path_XZ)
        N = path_traversal.find_longer_path_first_step(G, X, Y, Z, current_steps_X_to_Z)
        
        if N:
            
            #find separately to force our path down N instead of Y
            path_XN = path_traversal.find_path(G, X, N, prioritize_oneway)
            path_NZ = path_traversal.find_path(G, N, Z, prioritize_oneway)

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