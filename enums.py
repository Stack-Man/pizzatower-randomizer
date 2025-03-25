from enum import Enum

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