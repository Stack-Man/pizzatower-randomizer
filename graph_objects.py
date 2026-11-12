#Author: Stack Man
#Date: 11/1/2026

#Class structure to use as nodes pr edges in an nx graph to store information about the node or edge

from enums import DoorType, DoorDir, StartExitType, TraversalType
from objects import Path

from enum import Enum

from colors import ERROR, RESET, WARNING

import networkx as nx


class Node():
    def __init__(self, se_type: StartExitType):

        self.se_type = se_type #helps enforce a movement direction from path edge to transition edge

        #Dictionary of lists, for each destination DoorNode, hold a list of EdgeTraversals
        self.steps : dict[DoorNode, list[EdgeTraversal]] = {}
        
        #helper dicts for Flow algorithm
        self.next_steps : dict[DoorNode, list[EdgeTraversal]] = {}
        self.last_steps : dict[DoorNode, list[EdgeTraversal]] = {}

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

    def __eq__(self, other):
        if (type(other) != DoorNode):
            return False

        return self.door_type == other.door_type and self.door_dir == other.door_dir and self.se_type == other.se_type

    def __hash__(self):
        return hash((self.door_type, self.door_dir, self.se_type))

    def __str__(self):
        return str(self.door_type.value) + " " + str(self.door_dir.value) + " " + str(self.se_type.value)
        #return "(" + str(self.door_type.value) + ", " + str(self.door_dir.value) + ", " + str(self.se_type.value) + ")"
    
    def __contains__(self, item):
        return item == self

class CombinedDoorNode(Node):
    def __init__(self, nodes: list[DoorNode], se_type: StartExitType):
        super().__init__(se_type)

        self.nodes = nodes

    def __eq__(self, other):

        if (type(other) != CombinedDoorNode):
            return False

        #all nodes in self in other
        for n in self.nodes:
            if n not in other.nodes:
                return False

        #other does not contain nodes not in self
        if len(self.nodes) != len(other.nodes):
            return False

        #final sanity check
        if self.se_type == other.se_type:
            return True

    #combine the hash results of the list into a single tuple and hash that
    def __hash__(self):
        return hash(tuple(hash(node) for node in self.nodes))

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

class EdgeTraversal():
    def __init__(self, edges: list[Edge], rarity : float, traversal_type: TraversalType = TraversalType.ANY):
        self.edges = edges
        self.rarity = rarity
        self.traversal_type = traversal_type

        #initialize bipartite graphs for use later during impossible-booking exclusion and path selection
        self.bipartiteTW = nx.Graph()
        self.bipartitePT = nx.Graph()
        self.bipartiteNPT = nx.Graph()

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

    def contains(self, node: DoorNode):
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

#Manage DB and non DB lists of a traversal type in a single structure
class PathList():
    def __init__(self, P: list[Path]):
        print(f"{WARNING}WARNING: PathList is_double_bookable does not consider NDB size!")
        self.NDB : list[Path] = []
        self.DB : list[Path] = []

        for p in P:
            if (p.is_double_bookable):
                #print(f"add {p} to DB")
                self.DB.append(p)
            else:
                #print(f"add {p} to NDB")
                self.NDB.append(p)

    def __iter__(self):
        for p in self.NDB:
            yield p

        for p in self.DB:
            yield p

    def is_double_bookable(self):
        return len(self.DB) > 0 and len(self.NDB) == 0

    def __len__(self):
        return len(self.NDB) + len(self.DB)

    def pick_path(self):
        print(f"{WARNING}WARNING: pick_path in PathList in graph_objects.py is not implemente   d!")

        path = self.get_random_path(self.NDB)

        return path

    def get_random_path(self, paths: list[Path]):
        return paths.pop()
        

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

    #edge must have at least one path valid for the traversal type to be used
    def has_zero(self, traversal_type: TraversalType):
        match traversal_type:
            case TraversalType.ANY:
                return len(self.TW) > 0
            case TraversalType.NOTPIZZATIME:
                return len(self.NPT) > 0 or len(self.OW) > 0 or len(self.TW) > 0
            case TraversalType.PIZZATIME:
                return len(self.PT) > 0  or len(self.OW) > 0 or len(self.TW) > 0
            case TraversalType.OW:
                return len(self.OW) > 0 or len(self.TW) > 0


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

    def get_DB_paths(self, P: list[Path]):
        p_NDB = []
        p_DB = []

        for p in P:
            if (p.is_double_bookable):
                p_DB.append(p)
            else:
                p_NDB.append(p)

        return p_NDB, p_DB
    
    def pick_path(self, type: TraversalType):
        print(f"{WARNING}WARNING: pick_path in PathEdge in graph_objects.py is not implemented!")
        return self.TW.pick_path()
    
    def get_random_path(self, paths: list[Path]):
        return paths.pop()


    def __eq__(self, other):
        return self.start_node == other.start_node and self.end_node == other.end_node

    def __hash__(self):
        return hash((self.start_node, self.end_node))

class TransitionEdge(Edge):
    def __init__(self, start_node: DoorNode | CombinedDoorNode, end_node:  DoorNode | CombinedDoorNode):
        super().__init__(start_node, end_node)

        if (start_node.se_type is not StartExitType.EXIT or end_node.se_type is not StartExitType.START):
            print(f"{ERROR} ERROR: Transition Edge {start_node} to {end_node} is not EXIT to START {RESET}")

    def __eq__(self, other):
        return self.start_node == other.start_node and self.end_node == other.end_node
        
    def __hash__(self):
        return hash((self.start_node, self.end_node))
