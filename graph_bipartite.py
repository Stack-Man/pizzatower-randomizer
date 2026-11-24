#Author: Stack Man
#Date: 11/23/2026

#Custom bipartite graph implemention using adjaceny dicts to avoid
#overhead costs of networkx graphs when we process impossible bookings
#(typically 3k - 12k updates per selection, so minor overhead costs are significant)

from graph_objects import PathEdge, PathList

class BipartiteGraph():
    def __init__(self):
        #Two sets in the bipartite graph
        #Edge Nodes: Represent an edge in a traversal
        #Room Nodes: Represent a room, ID is room name
        #Edges from Edge show which rooms can be assigned to it

        #use adjacent dicts with sets to prevent redundant edges
        self.edge_nodes : dict[PathEdge, set[str]] = {}
        self.room_nodes : dict[str, set[PathEdge]] = {}
        self.matching : dict[PathEdge, str] = {}

    #add edge only if DB, for initial construction of EdgeTraverals
    def add_edge_if_DB(self, edge: PathEdge, path_lists: list[PathList]):

        has_at_least_one_path = False
                
        for PL in path_lists:

            #skip empty lists
            #they should not effect DB status
            if (len(PL) == 0):
                continue

            #if all lists are empty, invalid
            has_at_least_one_path = True

            if not PL.is_double_bookable():
                return False #Failed to ADD, edge must be DB

        if (not has_at_least_one_path):
            return False #Failed to ADD, edge must have at least one path

        self.add_edge(edge, path_lists)

        return True

    def add_edge(self, edge: PathEdge, path_lists: list[PathList]):
        
        if (edge in self.edge_nodes):
            raise LookupError(f"Tried to ADD {edge} already in BG")

        self.edge_nodes.setdefault(edge, set())

        self.add_or_update_edge(edge, path_lists)

    def remove_edge(self, edge: PathEdge):

        if (edge not in self.edge_nodes):
            raise LookupError(f"Tried to REMOVE {edge} NOT in BG")

        Rs = self.edge_nodes[edge]

        #We can leave isolated R nodes without issue
        for R in Rs:
            self.room_nodes[R].remove(edge)

        self.edge_nodes.pop(edge)

    def update_edge(self, edge: PathEdge, path_lists: list[PathList]):

        if (edge not in self.edge_nodes):
            raise LookupError(f"Tried to UPDATE {edge} not in BG")

        self.add_or_update_edge(edge, path_lists)
        
    def add_or_update_edge(self, edge: PathEdge, path_lists: list[PathList]):
        Rs = self.get_room_names(path_lists)

        #set up adjacencies
        #all Rs to E
        #and E to each R
        #set and dict automatically handles duplicates
        for R in Rs:
            self.edge_nodes[edge].add(R)

            self.room_nodes.setdefault(R, set())
            self.room_nodes[R].add(edge)

    def get_room_names(self, path_lists: list[PathList]):

        #prevent duplicate names with a set
        names : set[str] = set()

        for PL in path_lists:
            for P in PL.DB: #only DB rooms are added
                names.add(P.room_name)

        return names

    def check_for_valid_matching(self):
        # Matchings in both directions
        E_match : dict[PathEdge, str] = {}
        R_match : dict[str, PathEdge] = {}

        INF = float("inf")

        def BFS():
            to_visit : list[PathEdge] = []
            distance : dict[PathEdge, float] = {}

            #queue unmatched nodes to visit
            for E in self.edge_nodes:
                if E not in E_match:
                    distance[E] = 0
                    to_visit.append(E)
                else:
                    distance[E] = INF #use INF as marker for unvisited matched nodes

            shortest = INF

            while len(to_visit) > 0:
                E = to_visit.pop(0) #from front

                #skip distances longer than our shortest
                if distance[E] >= shortest:
                    continue

                for R in self.edge_nodes[E]:
                    matched_E = R_match.get(R) #get the E assigned to R (if any)

                    #R is unassigned
                    #if this occurs for all Rs of all unmatched Es
                    #then shortest is never reassigned and stays INF
                    if matched_E is None:
                        shortest = distance[E] + 1 #current cumulative distance record for unmatched Es

                    #Marker that E was matched but not visited in the current BFS
                    elif distance[matched_E] == INF:
                        distance[matched_E] = distance[E] + 1
                        to_visit.append(matched_E)

            #return distances and the shortest distance found
            return distance, shortest

        # DFS: Find augmenting paths using BFS distances
        def DFS(E : PathEdge, distance : dict[PathEdge, float], shortest: float):
            for R in self.edge_nodes[E]:
                matched_E = R_match.get(R)

                #assign R to E if R is unassigned
                if matched_E is None:
                    if distance[E] + 1 == shortest:
                        E_match[E] = R
                        R_match[R] = E
                        return True

                #R is assigned, check if we can reassign its E
                #to a deeper layer
                #We can only do this if the distance of the matched E is 
                #one more than the shortest distance of our current E
                elif distance.get(matched_E, INF) == distance[E] + 1:
                    if DFS(matched_E, distance, shortest):

                        #successfully reassigned R's original match 
                        #now assign R to E
                        
                        E_match[E] = R
                        R_match[R] = E
                        return True

            #failed to 
            distance[E] = INF

            return False

        # Hopcroft-Karp main loop
        while True:

            #create an alternating BFS and find
            #store shortest distance for each matched E from an unmatched E
            #and record the shortest of all of them
            distance, shortest = BFS()

            #BFS never found an augmented path
            #we've reached a perfect matching or cannot make one
            if shortest == INF:
                break

            for E in self.edge_nodes:
                if E not in E_match:
                    DFS(E, distance, shortest)

        # Check whether every edge node was matched
        if len(E_match) != len(self.edge_nodes):
            self.matching = {}
            return False

        self.matching = E_match
        return True

