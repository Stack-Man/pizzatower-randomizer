from enum import Enum
from json_keys import *

class BranchType(Enum):
    NONE = 0
    START = 1
    END = 2
    ANY = 3
    MID = 4
 
class PathTime(Enum):
    BOTH = 0
    PIZZATIME = 1
    NOTPIZZATIME = 2
    ANY = 3 #Allows selecting any PathTime
    
class DoorType(Enum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2
    DOOR = 3
    BOX = 4
    SECRET = 5
    ROCKET = 6
    TAXI = 7
    UPDOWN = 8      #For option to match doors directionally only
    LEFTRIGHT = 9
    ANY = 10
    
class DoorDir(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    ANY = 5

class AccessType(Enum):
    ANY = 0
    STARTONLY = 1
    EXITONLY = 2

class RoomType(Enum):
    ANY = 0
    NORMAL = 1
    BRANCH = 2
    ENTRANCE = 3
    JOHN = 4
    LOOP = 5

def get_dir(door):
    door_dir = door.get(DOOR_DIR)
    
    if door_dir is None:
        return DoorDir.NONE
    elif door_dir == "up":
        return DoorDir.UP
    elif door_dir == "down":
        return DoorDir.DOWN
    elif door_dir == "left":
        return DoorDir.LEFT
    elif door_dir == "right":
        return DoorDir.RIGHT
    else:
        return DoorDir.ANY

def flip_dir(door_dir):
    if door_dir == DoorDir.UP:
        return DoorDir.DOWN
    elif door_dir == DoorDir.DOWN:
        return DoorDir.UP
    elif door_dir == DoorDir.LEFT:
        return DoorDir.RIGHT
    elif door_dir == DoorDir.RIGHT:
        return DoorDir.LEFT
    else:
        return dir

def get_path_time(door):
    if (DOOR_PIZZATIME in door):
        return PathTime.PIZZATIME
    elif (DOOR_NOTPIZZATIME in door):
        return PathTime.NOTPIZZATIME
    else:
        return PathTime.BOTH
