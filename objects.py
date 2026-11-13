from enums import *
from colors import ERROR, RESET
from typing import Any
#from graph_objects import PathEdge, DoorNode

"""A door is an entrance or exit in a room.
    String  letter              : Game letter associated with this door. ROCKET or TAXI for those doors.
    Enum    door_type           : Transition type of this door (VERTICAL, HORIZONTAL, DOOR, BOX, SECRET, ROCKET, TAXI, NONE)
    Enum    door_dir            : Direction this door faces. (UP DOWN LEFT RIGHT NONE)
    
    Bool    branch              : Whether this door is re-used in two paths as part of a branch room.
    Bool    is_branch_start     : specifically for branchmid rooms where a branch starts
    Bool    is_branch_end       : specifically for branchmid rooms where a branch starts
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
            self.start_path_time = PathTime.PIZZATIME
            self.exit_path_time = path_time
        else:
            self.start_path_time = path_time_if_start
            self.exit_path_time = path_time
            
        self.access_type = access_type
        self.is_loop = is_loop
        
    def __str__(self):
        return f"{self.letter}"

    def print_stats(self):
        print(f"    {self.letter}:")
        print(f"        {self.door_type}")
        print(f"        {self.door_dir}")
        print(f"        {self.start_path_time}")
        print(f"        {self.exit_path_time}")
        print(f"        {self.access_type}")

        if (self.is_loop): print(f"         loop")
        if (self.initially_blocked): print(f"       rat blocked")
        if (self.branch): print(f"      branch")
        if (self.branchstart): print(f"         branch start")
        if (self.branchend): print(f"       branch end")

    def get_type_as_tuple(self):
        return (self.door_type, self.door_dir)

"""A Path is a valid route between two Doors with a specific start and exit
    Door    start_door  : Start of the path.
    Door    exit_door   : End of path.
    Bool    oneway      : Whether the path can be backtracked or not.
    Bool    is_double_bookable: Whether the path is from a room that can be double-booked
    str     room_name   : Name of the room this path is from
"""
class Path():
    def __init__(self, start_door: Door, exit_door: Door, oneway: bool, loop: bool):
        self.start_door = start_door
        self.exit_door = exit_door
        self.oneway = oneway
        self.is_loop = loop
        self.is_double_bookable = False
        self.room_name = "" #apply room name when adding paths to room

        #apply room when adding paths to room 
        #deepcopy automatically prevents circular deep copying with this ref
        #used during room selection to flush out all paths of a consumed DB room
        self.room : Room = Room("", [], [], False, False, False, False)

        #apply edge when adding paths to edge
        #used during room selection to quickly flush out all paths of a DB room from their respective edges
        #don't initialize here to prevent circular import
        #dummy_node = DoorNode(DoorType.NONE, DoorDir.NONE, StartExitType.START)
        #self.edge : PathEdge = PathEdge(dummy_node, dummy_node)
        self.edge : Any = None

    def __str__(self):
        return f"{self.start_door} to {self.exit_door}"

    def print_stats(self):
        print(f"    {self.start_door.letter} > {self.exit_door.letter}")

    def path_time(self):
        if (self.start_door.start_path_time != PathTime.BOTH):
            return self.start_door.start_path_time
        else:
            return self.exit_door.exit_path_time

    def inconsistent_path_time(self):
        return (self.start_door.start_path_time != self.exit_door.exit_path_time 
            and self.start_door.start_path_time != PathTime.BOTH 
            and self.exit_door.exit_path_time != PathTime.BOTH)
                        
        

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
              ---> exit
    
    "END" (exit is reused)
    
    leave    <---             
                  |- exit
    entrance --->/
        
    "ANY" (branching door can be used as entrance or exit)
    
    "MID" (neither entrance nor exit reuse is possible)
        IE: there are two mutually exclusive paths in different times in the same room.
        In this scenario, the not pizzatime path is used *during* another branch's sequence.
        On return, the return path is used to connect to the parent branch's return.
      
              /---> exit --> mid branch entrance --> mid exit
    entrance-|              
              <--- return <-- mid branch leave <-- mid return
"""
class Room():
    def __init__(self, name, doors, paths : list[Path], john, entrance, is_forced_branch_any, is_forced_branch_start):
        self.name = name
        self.doors = doors
        self.paths = paths
        self.branch_type = BranchType.ANY
        self.room_type = RoomType.ANY
        self.has_john = john
        self.has_entrance = entrance
        self.is_forced_branch_any = is_forced_branch_any
        self.is_forced_branch_start = is_forced_branch_start
        self.is_double_bookable = False

        for path in self.paths:
            path.room_name = name
            path.room = self

            if (path.inconsistent_path_time() and not john and not entrance):
                print(f"{ERROR} ERROR: Path of {name} from {path.start_door} to {path.exit_door} does not have consistent path times {path.start_door.start_path_time} to {path.exit_door.exit_path_time}{RESET}")
        
    def __str__(self):
        return f"{self.name}"
        
    def print_stats(self):
        print(f"Name: {self.name}")
        print(f"   Room: {self.room_type}")
        if (self.branch_type is not BranchType.NONE): print(f"   Branch: {self.branch_type}")
        if (self.has_john): print(f"   John: {self.has_john}")
        if (self.has_entrance): print(f"   Entr: {self.has_entrance}")

    def print_doors(self):
        if (self.doors is None or len(self.doors) <= 0):
            return

        print(f"    Doors:")

        for d in self.doors:
            d.print_stats()

    def print_paths(self):
        if (self.paths is None or len(self.paths) <= 0):
            return

        print(f"    Paths:")

        for p in self.paths:
            p.print_stats()
