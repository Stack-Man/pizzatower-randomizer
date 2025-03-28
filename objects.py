#Author: Stack Man
#Date: 3-25-2025

from enums import BranchType, PathTime, DoorType, DoorDir, AccessType, RoomType

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
    Connection to_connection            : The path used during not pizzatime.
    Connection return_connection        : The path used during pizzatime. NONE if to_connection is reused.
    Sequence   next_seqeunce            : The next sequence after to_connection.
    Room       first_room               : The room at the start of to_connection.
    Bool       first_room_is_end_branch : Necessary to clear ambiguity when first_room is BranchType.ANY
    
    
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
        Room: first_room,
        Bool: first_room_is_end_branch):
        
        self.to_conection = to_connection
        self.return_connection = return_connection
        self.next_seqeunce = next_sequence
        self.first_room = last_room
        self.first_room_is_end_branch = first_room_is_end_branch

    def __str__(self):
        return f"    [Sequence: to: {self.to_conection}, return: {self.return_connection}] \n{self.next_seqeunce}"
    

"""A Connection is a series of linked objects defining an order of Rooms and a Path through each Room
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
	Enum	room_type	: Type of room.				   (ONEWAY, TWOWAY, BRANCH, ENTRANCE, JOHN, LOOP, WAREXIT, CTOPEXIT, CTOPENTRANCE)
    
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
def Room():
    def __init__(self, str: name, [Path]: paths, BranchType: branch_type, RoomType: room_type):
        self.name = name
        self.paths = paths
        self.branch_type = branch_type
		self.room_type = room_type
		
        
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
    
    Bool    is_branch           : Whether this door is re-used in two paths as part of a branch room.
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
        bool: is_branch,
        bool: initially_blocked, 
        PathTime: path_time,
        AccessType: access_type,
        PathTime: start_time,
        PathTime: exit_time):
        
        self.letter = letter
        self.door_type = door_type
        self.door_dir = door_dir
        self.is_branch = is_branch
        self.initially_blocked = initially_blocked
        self.path_time = path_time
        self.access_type = access_type
        self.start_time = start_time
        self.exit_time = exit_time
        
    def __str__(self):
        return f"{self.letter}"
        
"""RoomRequirements packages a RoomType and a BranchType
    Enum    room_type
    Enum    branch_type
"""
def RoomRequirements():
    def __init__(self,
        RoomType: room_type,
        BranchType: branch_type):
        
        self.room_type = room_type
        self.branch_type = branch_type
    
    def __str__(self):
        return "RoomReq: " + str(self.room_type) + ", " + str(self.branch_type)
        
"""ConnectionRequirements packages various attributes used to create a Connection
    Room                first_room
    Room                last_room
    PathRequirements    first_path_requirements     :reqs for the path in the first_room
    PathRequirements    between_path_requirements   :reqs for any other path
    PathRequirements    last_path_requirements      :reqs for the path in the last_room
"""
def ConnectionRequirements():
    def __init__(self, 
        Room: first_room, 
        Room: last_room, 
        PathRequirements: first_path_requirements,
        PathRequirements: between_path_requirements,
        PathRequirements: last_path_requirements):
        
        self.first_room = first_room
        self.last_room = last_room
        self.first_path_requirements = first_path_requirements
        self.between_path_requirements = between_path_requirements
        self.last_path_requirements = last_path_requirements
    
    def __str__(self):
        return f"{self.first_room} {self.first_path_requirements} -> {self.between_path_requirements} -> {self.last_room} {self.last_path_requirements}"


"""PathRequirements packages various attributes used to find a valid Path
    String  start_letter        :Empty if any is allowed
    String  exit_letter         :"" ""
    Bool    use_start_letter    :If False, exclude start_letter instead
    Bool    use_exit_letter     :"" ""
    Bool    start_use_branch    :If start Door.is_branch should be True
    Bool    exit_use_branch     :"" ""
    [Enum]  path_times          :allowed times for this path
"""
def PathRequirements():
    def __init__(self,
        [PathTime]: path_times,
        str: start_letter = "",
        str: exit_letter = "",
        bool: use_start_letter = True,
        bool: use_exit_letter = True,
        bool: start_use_branch = False,
        bool: exit_use_branch = False):
        
        self.start_letter = start_letter
        self.exit_letter = exit_letters
        self.use_start_letter = use_start_letter
        self.use_exit_letter = use_exit_letter
        self.start_use_branch = start_use_branch
        self.exit_use_branch = exit_use_branch
        self.path_times = path_times
    
    def __str__(self):      
        sb = " branch" if self.start_use_branch else ""
        eb = " branch" if self.exit_use_branch else ""
        
        us = "" if self.use_start_letter else "not "
        ue = "" if self.use_exit_letter else "not "
        
        sl = "any" if self.start_letter == "" else self.start_letter
        el = "any" if self.exit_letter == "" else self.exit_letter
        
        return f"{us}{sl}{sb} to {ue}{el}{eb}"