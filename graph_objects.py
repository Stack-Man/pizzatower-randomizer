#Author: Stack Man
#Date: 11/1/2026

#Class structure to use as nodes pr edges in an nx graph to store information about the node or edge

from enums import DoorType, DoorDir, StartExitType, TraversalType, PathTime
from json_objects import Path

from colors import ERROR, RESET, WARNING

#__eq__ implementations compare cached hashes if possible
#hashes are already hashes of the otherwise compared attributes
#so comparison is equivalent

class Node():
    def __init__(self, se_type: StartExitType):

        self.se_type = se_type #helps enforce a movement direction from path edge to transition edge

        #Dictionary of lists, for each destination DoorNode, hold a list of EdgeTraversals
        self.steps : dict[DoorNode | CombinedDoorNode, list[EdgeTraversal]] = {}
        
        #helper dicts for Flow algorithm
        self.next_steps : dict[DoorNode | CombinedDoorNode, list[EdgeTraversal]] = {}
        self.last_steps : dict[DoorNode | CombinedDoorNode, list[EdgeTraversal]] = {}

        #helper bool for graph_collapse.py
        self.combined = False

        #helpers for graph_collapse.py
        self.parents = []
        self.children = []

class DoorNode(Node):
    def __init__(self, door_type: DoorType, door_dir: DoorDir, se_type: StartExitType):
        super().__init__(se_type)

        self.door_type = door_type
        self.door_dir = door_dir

        #cache hash to avoid rehashing since types are immutable
        self._hash = hash((self.door_type, self.door_dir, self.se_type))

    def __eq__(self, other):
        return self._hash == other._hash

    def __hash__(self):
        return self._hash 

    def __str__(self):
        return str(self.door_type.value) + " " + str(self.door_dir.value) + " " + str(self.se_type.value)

    def __contains__(self, item):
        return item == self

class CombinedDoorNode(Node):
    def __init__(self, nodes: list[DoorNode], se_type: StartExitType):
        super().__init__(se_type)

        self.nodes = nodes

        #cache hash to avoid rehashing since types are immutable
        self._hash = hash(tuple(hash(node) for node in self.nodes))

    def __eq__(self, other):
        return self._hash == other._hash       

    #combine the hash results of the list into a single tuple and hash that
    def __hash__(self):
        return self._hash

    def __str__(self):
        msg = "("

        for node in self.nodes:
            msg += ", " + str(node)

        return msg + ")"

    def __contains__(self, item):
        return item in self.nodes


class Edge():
    def __init__(self, start_node: DoorNode | CombinedDoorNode, end_node: DoorNode | CombinedDoorNode):
        self.start_node = start_node
        self.end_node = end_node
        self.combined = False

    def __eq__(self, other):
            return self.start_node == other.start_node and self.end_node == other.end_node
    
    def __hash__(self):
        return hash((self.start_node, self.end_node))

    def __str__(self):
        return str(self.start_node) + "--" + str(self.end_node)

#Manage DB and non DB lists of a traversal type in a single structure
class PathList():
    def __init__(self, P: list[Path]):
        self.NDB : list[Path] = []
        self.DB : list[Path] = []

        for p in P:
            if (p.is_double_bookable):
                #print(f"add {p} to DB")
                self.DB.append(p)
            else:
                #print(f"add {p} to NDB")
                self.NDB.append(p)

    def __str__(self):
        msg = ""
        
        for NDB in self.NDB:
            msg += f"\n NDB: {NDB.room_name} {NDB} {NDB.edge}"

        for DB in self.DB:
            msg += f"\n DB: {DB.room_name} {DB} {DB.edge}"

        return msg

    def __iter__(self):
        for p in self.NDB:
            yield p

        for p in self.DB:
            yield p

    def remove(self, path: Path):
        try:
            self.NDB.remove(path)

            #must update if NDB moves from 1 to 0
            if (len(self.NDB) == 0):
                return True #depleted

        except Exception as e:
            pass

        try:
            self.DB.remove(path)

            #must update if NDB is 0 and DB count changed
            #DB must have changed if remove succeeded
            return (len(self.NDB) == 0)

        except Exception as e:
            pass

        return False

    def add(self, path: Path):
        if (path.is_double_bookable):
            self.DB.append(path)

            #update if NDB is 0 and DB count changed
            #DB must have changed if remove succeeded
            return len(self.NDB) == 0
            
        else:
            self.NDB.append(path)

            #must update if NDB moves from 0 to 1
            if (len(self.NDB) == 1):
                return True #replenished

    def is_double_bookable(self):
        return len(self.DB) > 0 and len(self.NDB) == 0

    def __len__(self):
        return len(self.NDB) + len(self.DB)


class PathEdge(Edge):
    def __init__(self, start_node: DoorNode | CombinedDoorNode, end_node:  DoorNode | CombinedDoorNode):
        super().__init__(start_node, end_node)

        if (start_node.se_type is not StartExitType.START or end_node.se_type is not StartExitType.EXIT):
            print(f"{ERROR} ERROR: Path Edge {start_node} to {end_node} is not START to EXIT {RESET}")

        #four categories ensures no path appears in more than one list
        #while also allowing each traversal type to exclude invalid rooms
        #TW : TWANY only
        #NPT: NPT or OWANY
        #PT : PT or OWANY

        #Maintain two separate lists for DB and non DB paths so we can
        #quickly access and check the count of each. Use PathList to maintain those lists

        self.TW = PathList([])
        self.OW = PathList([])
        self.NPT = PathList([])
        self.PT = PathList([])

        self._hash = hash((self.start_node, self.end_node))

    def get_path_lists(self, traversal_type: TraversalType):
        match traversal_type:
            case TraversalType.ANY:
                return [self.TW]
            case TraversalType.NOTPIZZATIME:
                return [self.NPT, self.OW, self.TW]
            case TraversalType.PIZZATIME:
                return [self.PT, self.OW, self.TW]
            case TraversalType.OW:
                return [self.OW, self.TW]
            case _:
                raise NotImplementedError(f"select_rooms_from_matching not implemented for {traversal_type}")

    #edge must have at least one path valid for the traversal type to be used
    def has_zero(self, traversal_type: TraversalType):
        match traversal_type:
            case TraversalType.ANY:
                return len(self.TW) <= 0
            case TraversalType.NOTPIZZATIME:
                return len(self.NPT) <= 0 and len(self.OW) <= 0 and len(self.TW) <= 0
            case TraversalType.PIZZATIME:
                return len(self.PT) <= 0 and len(self.OW) <= 0 and len(self.TW) <= 0
            case TraversalType.OW:
                return len(self.OW) <=0 and len(self.TW) <= 0

    def count_DB(self, paths: list[Path]):
        db = 0
        notDB = 0

        for p in paths:
            if not p.is_double_bookable:
                notDB += 1
            else:
                db += 1

        return db, notDB
    
    def set_paths(self, TW: list[Path], OW: list[Path], PT: list[Path], NPT: list[Path]):
        self.TW = PathList(TW)
        self.OW = PathList(OW)
        self.NPT = PathList(PT)
        self.PT = PathList(NPT)

        lists = [TW, OW, PT, NPT]

        #store ref to edge in each path
        #to quickly flush out DB paths when a DB room is consumed
        for list in lists:
            for path in list:
                path.edge = self

    def remove(self, path: Path):
        lists = [self.TW, self.OW, self.PT, self.NPT]

        depleted = False

        for pl in lists:
            pl_depleted = pl.remove(path)
            depleted = depleted or pl_depleted

        return depleted

    def add(self, path: Path):
        replenished = False
        
        if (path.get_path_time() == PathTime.BOTH):
            if (not path.oneway):
                replenished = self.TW.add(path)
            else:
                replenished = self.OW.add(path)
        elif (path.get_path_time() == PathTime.NOTPIZZATIME):
            replenished = self.NPT.add(path)
        else:
            replenished = self.PT.add(path)

        return replenished
    
    def get_DB_paths(self, P: list[Path]):
        p_NDB = []
        p_DB = []

        for p in P:
            if (p.is_double_bookable):
                p_DB.append(p)
            else:
                p_NDB.append(p)

        return p_NDB, p_DB

    def __eq__(self, other):
        return self._hash == other._hash #self.start_node == other.start_node and self.end_node == other.end_node

    def __hash__(self):
        return self._hash

class TransitionEdge(Edge):
    def __init__(self, start_node: DoorNode | CombinedDoorNode, end_node:  DoorNode | CombinedDoorNode):
        super().__init__(start_node, end_node)

        if (start_node.se_type is not StartExitType.EXIT or end_node.se_type is not StartExitType.START):
            print(f"{ERROR} ERROR: Transition Edge {start_node} to {end_node} is not EXIT to START {RESET}")

        self._hash = hash((self.start_node, self.end_node))

    def __eq__(self, other):
        return self._hash == other._hash #return self.start_node == other.start_node and self.end_node == other.end_node
        
    def __hash__(self):
        return  self._hash


#Author: Stack Man
#Date: 11/23/2026

#Custom bipartite graph implemention using adjaceny dicts to avoid
#overhead costs of networkx graphs when we process impossible bookings
#(typically 3k - 12k updates per selection, so minor overhead costs are significant)

#from graph_objects import PathEdge, PathList

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

    def __contains__(self, item):
        return item in self.edge_nodes

    #When extending an EdgeTraversal into a new one
    #we need to make copies of its current BGs
    #a shallow copy is all that is needed, the insides should
    #reference the same PathEdge objects
    def copy(self):
        copy = BipartiteGraph()

        copy.edge_nodes = self.edge_nodes.copy()
        copy.room_nodes = self.room_nodes.copy()
        copy.matching = self.matching.copy()

        return copy


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

        Rs = self.get_room_names(path_lists)
        
        #set up adjacencies
        #all Rs to E
        #and E to each R
        #set and dict automatically handles duplicates
        for R in Rs:
            self.edge_nodes[edge].add(R)

            self.room_nodes.setdefault(R, set())
            self.room_nodes[R].add(edge)

    def remove_edge(self, edge: PathEdge):

        if (edge not in self.edge_nodes):
            raise LookupError(f"Tried to REMOVE {edge} NOT in BG")

        Rs = self.edge_nodes[edge]

        #We can leave isolated R nodes without issue
        for R in Rs:
            if R in self.room_nodes and edge in self.room_nodes[R]:
                self.room_nodes[R].remove(edge)

        self.edge_nodes.pop(edge)

    def update_edge(self, edge: PathEdge, path_lists: list[PathList]):

        if (edge not in self.edge_nodes):
            raise LookupError(f"Tried to UPDATE {edge} not in BG")

        prev_Rs : set[str] = self.edge_nodes[edge]
        to_remove : set[str] = set()

        Rs = self.get_room_names(path_lists)

        #remove edge from R not in edge anymore
        for R in prev_Rs:
            if R not in Rs:
                to_remove.add(R)
                
                try:
                    self.room_nodes[R].remove(edge)
                except:
                    continue

        #remove from edge any R not in Rs
        for R in to_remove:
            try:
                self.edge_nodes[edge].remove(R)
            except:
                continue
                
        #add Rs to edge and edge to each R
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

        #store to avoid resorted lists more than once per matching
        E_nodes = sorted(self.edge_nodes, key=lambda x : x._hash)
        sorted_Rs : dict[PathEdge, list[str]] = {}

        def BFS():
            to_visit : list[PathEdge] = []
            distance : dict[PathEdge, float] = {}

            #queue unmatched nodes to visit
            for E in E_nodes:
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

                #sort by string
                #indexed to avoid resorts in same matching
                Rs_of_E = sorted_Rs.setdefault(E, sorted(self.edge_nodes[E], key=lambda x: x))

                for R in Rs_of_E:
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

            Rs_of_E = sorted_Rs.setdefault(E, sorted(self.edge_nodes[E], key=lambda x: x))
            
            for R in Rs_of_E:
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

            for E in E_nodes:
                if E not in E_match:
                    DFS(E, distance, shortest)

        # Check whether every edge node was matched
        if len(E_match) != len(self.edge_nodes):
            self.matching = {}
            return False

        self.matching = E_match
        return True


class EdgeTraversal():
    def __init__(self, edges: list[Edge], traversal_type: TraversalType = TraversalType.ANY):
        self.edges = edges
        self.traversal_type = traversal_type

        #initialize bipartite graphs for use later during impossible-booking exclusion and path selection
        self.bipartiteTW = BipartiteGraph()
        self.bipartitePT = BipartiteGraph()
        self.bipartiteNPT = BipartiteGraph()

        #record updated edges set in traversal
        #and update it before accessing
        self.to_update : set[PathEdge] = set()

        #raise NotImplementedError(f"EdgeTraversal does not implement update before access!")

    def get_matching(self, traversal_type: TraversalType):

        if (traversal_type == TraversalType.ANY):
            return self.bipartiteTW.matching
        elif (traversal_type == TraversalType.PIZZATIME):
            return self.bipartitePT.matching
        elif (traversal_type == TraversalType.NOTPIZZATIME):
            return self.bipartiteNPT.matching
        else:
            raise NotImplementedError(f"EdgeTraversal get_matching not implemented for {traversal_type}")
        

    def __iter__(self):
        for e in self.edges:
            yield e

    def has_no_zero_edges(self):
        for edge in self.edges:
            if (type(edge) == TransitionEdge):
                continue

            if (type(edge) == PathEdge):
                if edge.has_zero(self.traversal_type):
                    return False

        return True
    
    def __len__(self):
        return len(self.edges)

    def __contains__(self, item):
        return item in self.edges

    def contains(self, node: DoorNode | CombinedDoorNode):
        for edge in self.edges:
            if (edge.start_node == node or edge.end_node == node):
                return True

        return False

    def contains_subset(self, subset):
        if (len(self) <= len(subset)):
            return False

        for edge in subset.edges:
            if edge not in self.edges:
                return False

        return True
    

    def __str__(self):
        msg = ""

        for edge in self.edges:

            msg = msg + str(edge) + " > "

        return msg


