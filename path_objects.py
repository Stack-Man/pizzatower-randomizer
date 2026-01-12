class RoomPath():
    def __init__(self, room_name, start_letter, exit_letter, is_oneway):
        self.room_name = room_name
        self.start_letter = start_letter
        self.exit_letter = exit_letter
        self.is_oneway = is_oneway
    
    def __str__(self):
        return f"{self.room_name} {self.start_letter}{self.exit_letter}"

class Endpoint():
    def __init__(self, node):
        self.door_type = node.inner_id.door_type
        self.door_dir = node.inner_id.door_dir
        self.start_exit_type = node.inner_id.start_exit_type
        self.steps = {}
        self.next_steps = {}
        
        self.steps["NO STEPS SET"] = "NO STEPS SET"
    
    def __str__(self):
        return f"{se(self.start_exit_type)} {dt(self.door_type)} {dd(self.door_dir)}"
    
    def __eq__(self, other):
        if not isinstance(other, Endpoint):
            return NotImplemented
        
        return self.door_type == other.door_type and self.door_dir == other.door_dir and self.start_exit_type == other.start_exit_type
        """if not isinstance(other, Endpoint):
            return NotImplemented

        return (
            getattr(self, "door_type", None) == getattr(other, "door_type", None)
            and getattr(self, "door_dir", None) == getattr(other, "door_dir", None)
            and getattr(self, "start_exit_type", None) == getattr(other, "start_exit_type", None)
        )"""
    
    def __hash__(self):
        return hash((self.door_type, self.door_dir, self.start_exit_type))
        
        """
        return hash((
            getattr(self, "door_type", None),
            getattr(self, "door_dir", None),
            getattr(self, "start_exit_type", None),
        ))"""

from node_id_objects import StartExitType
from enums import DoorType, DoorDir

def se(type):
    if type == StartExitType.START:
        return "START"
    else:
        return "EXIT"

def dt(type):
    if type == DoorType.DOOR:
        return "DOOR"
    elif type == DoorType.HORIZONTAL:
        return "HALL"
    elif type == DoorType.VERTICAL:
        return "FALL"
    elif type == DoorType.BOX:
        return "BOX"
    else:
        return type

def dd(type):
    if type == DoorDir.LEFT:
        return "LEFT"
    elif type == DoorDir.RIGHT:
        return "RIGHT"
    elif type == DoorDir.UP:
        return "UP"
    elif type == DoorDir.DOWN:
        return "DOWN"
    elif type == DoorDir.NONE:
        return "NONE"
    else:
        return type








