from enums import *

"""A Room contains a list of paths that can go through that room.
    String  name        : Name of the room
    [Door]  doors       : A list of Door
    [Path]  paths       : A list of Path.
    Enum    branch_type : Type of branch this room is. (NONE, START, END, ANY, or MID). Branch type is enforced by in game obstacles.
    Enum    room_type   : Type of room.                   (NORMAL, BRANCH, ENTRANCE, JOHN, LOOP)
    Bool    has_john    : If a John pillar is present in the room
    Bool    has_entrance: If an entrance door is present in the room
    
    A "branch" room has two paths. One for pizzatime and one for not.
    
    "START" (entrance is reused)
        
              /<--- return
    entrance-|
              \---> exit
    
    "END" (exit is reused)
    
    leave    <---\             
                  |- exit
    entrance --->/
        
    "ANY" (branching door can be used as entrance or exit)
    
    "MID" (neither entrance nor exit reuse is possible)
        IE: there are two mutually exclusive paths in different times in the same room.
        In this scenario, the not pizzatime path is used *during* another branch's sequence.
        On return, the return path is used to connect to the parent branch's return.
      
              /---> exit --> mid branch entrance --> mid exit
    entrance-|              
              \<--- return <-- mid branch leave <-- mid return
"""
class Room():
    def __init__(self, name, doors, paths, john, entrance):
        self.name = name
        self.doors = doors
        self.paths = paths
        self.branch_type = None
        self.room_type = None
        self.has_john = john
        self.has_entrance = entrance
        
        
    def __str__(self):
        return f"{self.name}"


"""A door is an entrance or exit in a room.
    String  letter              : Game letter associated with this door. ROCKET or TAXI for those doors.
    Enum    door_type           : Transition type of this door (VERTICAL, HORIZONTAL, DOOR, BOX, SECRET, ROCKET, TAXI, NONE)
    Enum    door_dir            : Direction this door faces. (UP DOWN LEFT RIGHT NONE)
    
    Bool    branch              : Whether this door is re-used in two paths as part of a branch room.
    Bool    initially_blocked   : Whether this door must be used first before back-tracking is possible. (IE rat obstacle).
    Enum    start_path_time     : When this door is accessible as a start (BOTH, PIZZATIME, NOTPIZZATIME)
    Enum    exit_path_time      : When this door is accessible as an exit (BOTH, PIZZATIME, NOTPIZZATIME)
    
    Enum    access_type         : How this door can be used (ANY, STARTONLY, EXITONLY)
"""
class Door():
    def __init__(self,
        letter: str,
        door_type: DoorType,
        door_dir: DoorDir,
        branch: bool,
        is_branch_start: bool,
        is_branch_end: bool,
        initially_blocked: bool,
        path_time: PathTime,
        access_type: AccessType,
        path_time_if_start: PathTime,
        if_notpizzatime_exit_only: bool,
        is_loop: bool):

        self.letter = letter
        self.door_type = door_type
        self.door_dir = door_dir
        self.branch = branch
        self.branchstart = is_branch_start
        self.branchend = is_branch_end
        self.initially_blocked = initially_blocked
        
        #Convert special parameters into individual path time
        #for start and exit
        if if_notpizzatime_exit_only:
            self.start_path_time = PathTime.pizzatime
            self.exit_path_time = path_time
        else:
            self.start_path_time = path_time_if_start
            self.exit_path_time = path_time
            
        self.access_type = access_type
        self.is_loop = is_loop
        
    def __str__(self):
        return f"{self.letter}"

"""A Path is a valid route between two Doors with a specific start and exit
    Door    start_door  : Start of the path.
    Door    exit_door   : End of path.
    Enum    path_time   : When this path is accessible (BOTH, PIZZATIME, NOTPIZZATIME).
                          The reverse path is a separate path object
    Bool    oneway      : Whether the path can be backtracked or not.
"""
class Path():
    def __init__(self, start_door: Door, exit_door: Door, path_time: PathTime, oneway: bool, loop: bool):
        self.start_door = start_door
        self.exit_door = exit_door
        self.path_time = path_time
        self.oneway = oneway
        self.loop = loop
    
    def __str__(self):
        return f"{self.start_door} to {self.exit_door}"