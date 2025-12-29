from enum import Enum
from enums import *

#Objects used as the indexes of the nodes in layers
#identifies type of node
#and specific qualities of the transition ro door in inner_id
#although they are objects, the eq comparison uses their contents so that comparison can be made
#without the object itself

#TODO: test


class NodeType(Enum):
    NONE = 0
    TRANSITION = 1
    DOOR = 2
    ROOM = 3

class Node_ID():
    
    def __init__(self, layer_id, node_type: NodeType, inner_id):
        self.layer_id = layer_id 
        self.node_type = node_type
        self.inner_id = inner_id
        
        
    def __str__(self):
        #return f"N: {self.layer_id} {str(self.node_type)} \n({str(self.inner_id)})"
        return f"{str(self.inner_id)}"
    
    def __eq__(self, other):
        return self.layer_id == other.layer_id and self.node_type == other.node_type and self.inner_id == other.inner_id
    
    #necessary so that we can use it in a networkx graph
    def __hash__(self):
        return hash((self.layer_id, self.node_type, self.inner_id))

class StartExitType(Enum):
    NONE = 0
    START = 1
    EXIT = 2
    INITIAL = 3
    
class Transition_ID():
    
    def __init__(self, start_exit_type: StartExitType, door_type: DoorType, door_dir: DoorDir):
        self.start_exit_type = start_exit_type
        self.door_type = door_type
        self.door_dir = door_dir
    
    def __str__(self):
        return f"T: {str(self.door_type)} {str(self.door_dir)}"
    
    def __eq__(self, other):
        #print(f"compare {str(self)} to {str(other)}")
        
        return self.start_exit_type == other.start_exit_type and self.door_type == other.door_type and self.door_dir == other.door_dir

    def __hash__(self):
        return hash((self.start_exit_type, self.door_type, self.door_dir))

class Door_ID():
    
    def __init__(self, start_exit_type: StartExitType, room_id, letter):
        self.start_exit_type = start_exit_type
        self.room_id = room_id
        self.letter = letter
    
    def __str__(self):
        return f"D: ({str(self.room_id)}) {str(self.letter)}"
    
    def __eq__(self, other):
        return self.start_exit_type == other.start_exit_type and self.room_id == other.room_id and self.letter == other.letter
    
    def __hash__(self):
        return hash((self.start_exit_type, self.room_id, self.letter))


def create_door_node_id(layer_id, start_exit_type: StartExitType, room_id, letter):
    
    door_id = Door_ID(start_exit_type, room_id, letter)
    node_id = Node_ID(layer_id, NodeType.DOOR, door_id)
    
    return node_id

def create_transition_node_id(layer_id, start_exit_type: StartExitType, door_type: DoorType, door_dir: DoorDir):
    
    transition_id = Transition_ID(start_exit_type, door_type, door_dir)
    node_id = Node_ID(layer_id, NodeType.TRANSITION, transition_id)
    
    return node_id

def create_transition_id(start_exit_type: StartExitType, door_type: DoorType, door_dir: DoorDir):
    
    transition_id = Transition_ID(start_exit_type, door_type, door_dir)
    
    return transition_id

def create_room_node_id(layer_id, room_name):
    
    node_id = Node_ID(layer_id, NodeType.ROOM, room_name)
    
    return node_id












