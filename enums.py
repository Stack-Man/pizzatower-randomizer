from enum import Enum
from json_keys import *

class BranchType(Enum):
    NONE = 0
    START = 1
    END = 2
    ANY = 3
    MID = 4
    FORCED_ANY = 5
    FORCED_START = 6
 
class PathTime(Enum):
    BOTH = 0
    PIZZATIME = 1
    NOTPIZZATIME = 2
    
class DoorType(Enum):
    NONE = "NONE"
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"
    DOOR = "DOOR"
    BOX = "BOX"
    SECRET = "SECRET"
    ROCKET = "ROCKET"
    TAXI = "TAXI"
    LEVELDOOR = "LEVELDOOR"
    ANY = "ANY"
    
class DoorDir(Enum):
    NONE = "NONE"
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ANY = "ANY"

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

class StartExitType(Enum):
    START = "S"
    EXIT = "E"

class TraversalType(Enum):
    PIZZATIME = 0
    NOTPIZZATIME = 1
    OW = 2
    ANY = 3
    INVALID = 4

    