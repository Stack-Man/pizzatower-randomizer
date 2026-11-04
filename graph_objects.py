#Author: Stack Man
#Date: 11/1/2026

#Class structure to use as nodes pr edges in an nx graph to store information about the node or edge

from enums import DoorType, DoorDir
from objects import Path

from enum import Enum

from colors import ERROR, RESET


class StartExitType(Enum):
    START = "S"
    EXIT = "E"
    X = ""

class DoorNode():
    def __init__(self, door_type: DoorType, door_dir: DoorDir, se_type: StartExitType):
        self.door_type = door_type
        self.door_dir = door_dir
        self.se_type = se_type #helps enforce a movement direction from path edge to transition edge

        #Dictionary of lists, for each destination DoorNode, hold a list of EdgeTraversals
        self.steps : dict[DoorNode, list[EdgeTraversal]] = {}

        #helper dicts for Flow algorithm
        self.next_steps : dict[DoorNode, list[EdgeTraversal]] = {}
        self.last_steps : dict[DoorNode, list[EdgeTraversal]] = {}

    def __eq__(self, other):
        return self.door_type == other.door_type and self.door_dir == other.door_dir and self.se_type == other.se_type

    def __hash__(self):
        return hash((self.door_type, self.door_dir, self.se_type))

    def __str__(self):
        return str(self.door_type.value) + " " + str(self.door_dir.value)
        #return "(" + str(self.door_type.value) + ", " + str(self.door_dir.value) + ", " + str(self.se_type.value) + ")"

class Edge():
    def __init__(self, start_node: DoorNode, end_node: DoorNode):
        self.start_node = start_node
        self.end_node = end_node

    def __eq__(self, other):
            return self.start_node == other.start_node and self.end_node == other.end_node
    
    def __hash__(self):
        return hash((self.start_node, self.end_node))

    def __str__(self):
        return str(self.start_node) + "--" + str(self.end_node)

class EdgeTraversal():
    def __init__(self, edges: list[Edge], rarity : float, is_npt: bool, is_pt: bool, is_owany: bool):
        self.edges = edges
        self.rarity = rarity
        self.is_npt = is_npt
        self.is_pt = is_pt
        self.is_owany = is_owany

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




class PathEdge(Edge):
    def __init__(self, start_node: DoorNode, end_node: DoorNode):
        super().__init__(start_node, end_node)

        if (start_node.se_type is not StartExitType.START or end_node.se_type is not StartExitType.EXIT):
            print(f"{ERROR} ERROR: Path Edge {start_node} to {end_node} is not START to EXIT {RESET}")

        #four categories ensures no path appears in more than one list
        #while also allowing each traversal type to exclude invalid rooms
        #TW : TWANY only
        #NPT: NPT or OWANY
        #PT : PT or OWANY

        self.pathsTWANY : list[Path] = []
        self.pathsOWANY : list[Path] = []
        self.pathsPT : list[Path] = []
        self.pathsNPT : list[Path] = []

        

    def __eq__(self, other):
        return self.start_node == other.start_node and self.end_node == other.end_node

    def __hash__(self):
        return hash((self.start_node, self.end_node))

class TransitionEdge(Edge):
    def __init__(self, start_node: DoorNode, end_node: DoorNode):
        super().__init__(start_node, end_node)

        if (start_node.se_type is not StartExitType.EXIT or end_node.se_type is not StartExitType.START):
            print(f"{ERROR} ERROR: Transition Edge {start_node} to {end_node} is not EXIT to START {RESET}")

    def __eq__(self, other):
        return self.start_node == other.start_node and self.end_node == other.end_node
        
    def __hash__(self):
        return hash((self.start_node, self.end_node))
