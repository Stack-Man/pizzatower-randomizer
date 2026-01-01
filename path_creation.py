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

def find_path(G, A, F):
    return

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

def flow(G):
    return

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
1. For path AF of length N choose X, Y from [0, N] where Y > X
2. For at least one neighbor of X, look for at least one path XY where X + 1 in XY != X + 1 in AF and X+1[Y] >= X[Y]

3a. If such a path exists: For each room R of every path P in segment X to Y readd all paths from room R to the graph and reflow if any new edges were added
4a. Find Path XY where X + 1 in XY != X + 1 in AF and X+1[Y] >= X[Y]

3b. Else move X and Y and goto step 2
"""

def grow_path(path):
    return