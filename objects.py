#Author: Stack Man
#Date: 3-25-2025

from enums import BranchType, PathTime, DoorType, DoorDir, AccessType

"""A Level is a datatype that contains an intial sequence
    Room        entrance        : The first room in the level.
    Sequence    initial_sequence: The first sequence in the level.
"""
class Level():
    def __init__(self, Room: entrance, Sequence: initial_sequence):
        self.entrance: Room = entrance
        self.initial_sequence: Sequence = initial_sequence
    
    def __str__(self):
        return f"Level: {self.initial_sequence}"


"""A Sequence is a series of linked objects defining Connections between two "branch" rooms.
    Connection to_connection    : The path used during not pizzatime.
    Connection return_connection: The path used during pizzatime. NONE if to_connection is reused.
    Sequence   next_seqeunce    : The next sequence after to_connection.
    Room       last_room        : The room at the end of to_connection.
    Bool last_room_is_end_branch: Whether the last room is the end of a branch. #TODO: can we pass return_connection != NONE instead?
    
    
    [seq 1      ][seq 2            ][seq 3       ]
                          _return_
    [end] <-to-> [start] /        \ [end] <-to-> [start]
                         \_  to  _/
"""
class Sequence():
    def __init__(self, 
        Connection: to_connection, 
        Connection: return_connection,
        Sequence: next_sequence, 
        Room: last_room,
        Bool: last_room_is_end_branch):
        
        self.to_conection = to_connection
        self.return_connection = return_connection
        self.next_seqeunce = next_sequence
        self.last_room = last_room
        self.last_room_is_end_branch = last_room_is_end_branch

    def __str__(self):
        return f"    [Sequence: to: {self.to_conection}, return: {self.return_connection}] \n{self.next_seqeunce}"
    

"""A Connection is a series of linked objects defining a path through a series of rooms.
    Room        room            : The room this path is in.
    Path        path            : The path in this room that leads to the next room.
    Connection  next_connection : The connection that this path connects to.
"""
class Connection():
    def __init__(self, Room: room, Path: path, Connection: next_connection):
        self.room = room
        self.path = path
        self.next_connection = next_connection
    
    def __str__(self):
        return f"{self.room.name}: {self.path} --> {self.next_connection}"


"""A Room contains a list of paths that can go through that room.
    String  name        : Name of the room
    [Path]  paths       : A list of Path.
    Enum    branch_type : Type of branch this room is. (NONE, START, END, ANY, or MID). Branch type is enforced by in game obstacles.
    
    A "branch" room has two paths. One for pizzatime and one for not.
    
    "START" (entrance is reused)
        
              /<--- return
    entrance-|
              \---> exit
    
    "END" (exit is reused)
    
    leave    <---\             
                  |- exit
    entrance --->/
        
    "ANY" (either entrance or exit reuse is possible)
    
    "MID" (neither entrance nor exit reuse is possible)
        IE: there are two mutually exclusive paths in different times in the same room.
        In this scenario, the not pizzatime path is used *during* another branch's sequence.
        On return, the return path is used to connect to the parent branch's return.
      
              /---> exit --> mid branch entrance --> mid exit
    entrance-|              
              \<--- return <-- mid branch leave <-- mid return
"""
def Room():
    def __init__(self, str: name, [Path]: paths, BranchType: branch_type):
        self.name = name
        self.paths = paths
        self.branch_type = branch_type
        
    def __str__(self):
        return f"{self.name}"


"""A Path is a valid route between two Doors
    Door    start_door  : Start of the path.
    Door    exit_door   : End of path.
    Enum    path_time    : When this path is accessible (BOTH, PIZZATIME, NOTPIZZATIME).
    Bool    oneway      : Whether the path can be backtracked or not.
"""
def Path():
    def __init__(self, Door: start_door, Door: exit_door, PathTime: path_time, bool: oneway):
        self.start_door = start_door
        self.exit_door = exit_door
        self.path_time = path_time
        self.oneway = oneway
    
    def __str__(self):
        return f"{self.start_door} to {self.exit_door}"


"""A door is an entrance or exit in a room.
    String  letter              : Game letter associated with this door. ROCKET or TAXI for those doors.
    Enum    door_type           : Transition type of this door (VERTICAL, HORIZONTAL, DOOR, BOX, SECRET, ROCKET, TAXI, NONE)
    Enum    door_dir            : Direction this door faces. (UP DOWN LEFT RIGHT NONE)
    
    Enum    branch_type         : Whether this door is re-used in two paths as part of a branch room. (NONE, START, END, ANY)
    Bool    initially_blocked   : Whether this door must be used first before back-tracking is possible. (IE rat obstacle).
    Enum    path_time           : When this door is accessible (BOTH, PIZZATIME, NOTPIZZATIME)
    
    Enum    access_type         : How this door can be used (ANY, STARTONLY, EXITONLY)
    Enum    start_time          : When this door can be used if its a start (BOTH, PIZZATIME, NOTPIZZATIME)
    Enum    exit_time           : When this door can be used if its an exit (BOTH, PIZZATIME, NOTPIZZATIME)
"""
def Door():
    def __init__(self, 
        str: letter, 
        DoorType: door_type, 
        DoorDir: door_dir,
        BranchType: branch_type,
        bool: initially_blocked, 
        PathTime: path_time,
        AccessType: access_type,
        PathTime: start_time,
        PathTime: exit_time):
        
        self.letter = letter
        self.door_type = door_type
        self.door_dir = door_dir
        self.branch_type = branch_type
        self.initially_blocked = initially_blocked
        self.path_time = path_time
        self.access_type = access_type
        self.start_time = start_time
        self.exit_time = exit_time
        
    def __str__(self):
        return f"{self.letter}"