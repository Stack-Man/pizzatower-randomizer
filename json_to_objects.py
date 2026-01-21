from enums import *
from json_keys import *
from objects import *

#-------------------
#   JSON to Object
#-------------------

JSON_ROOMS = "rooms"
JSON_DOORS = "doors"
JSON_JOHN = "pillar"
JSON_ENTRANCE = "entrance"
JSON_ROOM_NAME = "title"

def json_to_rooms(json):
    
    json_rooms = json[JSON_ROOMS]
    rooms = []

    for json_room in json_rooms:
        room = json_to_room(json_room)
        rooms.append(room)
        
    return rooms

def json_to_room(json_room):
    is_john_room = JSON_JOHN in json_room
    is_entrance_room = JSON_ENTRANCE in json_room
    room_name = json_room[JSON_ROOM_NAME]
    
    doors = json_to_doors(json_room)
    
    print("Making paths of ", str(room_name))
    paths = doors_to_paths(doors, is_john_room)
    
    room = Room(room_name, doors, paths, is_john_room, is_entrance_room)
    
    room.branch_type = get_branch_type(room)
    room.room_type =  get_room_type(room)
    
    #TODO: check for CTOP Entrance, CTOP Exit, War EXIT
    
    return room
    
    
def json_to_doors(json_room):
    if JSON_DOORS not in json_room:
        return []
    
    doors = []
    json_doors = json_room[JSON_DOORS]
    
    for json_door in json_doors:
        door = json_to_door(json_door)
        doors.append(door)

    return doors

def json_to_door(json_door):
    
    letter = json_door.get(DOOR_LETTER)
    j_door_type = json_door.get(DOOR_TYPE)
    j_door_dir = json_door.get(DOOR_DIR)

    door_dir = get_dir(j_door_dir)
    door_type = get_door_type(j_door_type)

    is_branch = DOOR_BRANCH in json_door
    is_branch_start = DOOR_BRANCH_START in json_door
    is_branch_end = DOOR_BRANCH_END in json_door
    initially_blocked = DOOR_INITIALLY_BLOCKED in json_door
    
    path_time = get_path_time(json_door)
    
    access_type = AccessType.ANY

    if DOOR_START_ONLY in json_door:
        access_type = AccessType.STARTONLY
    elif DOOR_EXIT_ONLY in json_door:
        access_type = AccessType.EXITONLY
    
    #if used as a start, must be this time
    path_time_if_start = path_time

    if DOOR_PIZZATIMESTART in json_door:
        path_time_if_start = PathTime.PIZZATIME
    elif DOOR_NOTPIZZATIMESTART in json_door:
        path_time_if_start = PathTime.NOTPIZZATIME

    #if notpizzatime, must be used as an exit
    if_notpizzatime_exit_only = DOOR_NOTPIZZATIMEEXITONLY in json_door

    is_loop = DOOR_LOOP in json_door

    door = Door(letter,
                door_type,
                door_dir,
                is_branch,
                is_branch_start,
                is_branch_end,
                initially_blocked,
                path_time,
                access_type,
                path_time_if_start,
                if_notpizzatime_exit_only,
                is_loop)
    
    return door

#--------------------
#   Object to Object
#--------------------

def doors_to_paths(doors, is_john_room):
    paths = []
    
    #for every door
    for a in range(0, len(doors)):

        door_a = doors[a]

        #handle one door rooms
        c = a if len(doors) <= 1 else a + 1
        
        #for every door after that
        for b in range(c, len(doors)):

            door_b = doors[b]

            path_ab = doors_to_path(door_a, door_b, is_john_room)
            path_ba = doors_to_path(door_b, door_a, is_john_room)

            if path_ab != None:
                paths.append(path_ab)
            
            #don't double add loop paths
            if path_ba != None and door_a.letter != door_b.letter:
                paths.append(path_ba)
    
    return paths

def doors_to_path(start_door, exit_door, is_john_room):

    #start is exitonly or exit is startonly
    if start_door.access_type == AccessType.EXITONLY or exit_door.access_type == AccessType.STARTONLY:
        print("     PATH: ", start_door.letter, " TO ", exit_door.letter, " NOT VALID. BAD ACCESSTYPE")
        return None

    #path time mismatch, unless it is in a john room
    #path times of start and exit must match or at least one is BOTH
    
    one_is_both = start_door.start_path_time is PathTime.BOTH or exit_door.exit_path_time is PathTime.BOTH
    times_match = start_door.start_path_time is exit_door.exit_path_time
    
    if not is_john_room and not times_match and not one_is_both:
        print("     PATH: ", start_door.letter, " TO ", exit_door.letter, " NOT VALID. BAD TIME MATCH AND NOT JOHN")
        return None
    
    #oneway = start or exit only but not initially blocked
    #initially_blocked is processed from the door itself in the objects to graph stage
    is_oneway = (start_door.access_type == AccessType.STARTONLY and not start_door.initially_blocked) or (exit_door.access_type == AccessType.EXITONLY and not exit_door.initially_blocked)
    is_loop = start_door.is_loop or exit_door.is_loop

    path = Path(start_door, exit_door, is_oneway, is_loop)

    print("     PATH: ", path, ": oneway? ", is_oneway)

    return path

#-------------------
#   Object Helpers
#-------------------
def get_branch_type(room):
    #branchstart and branchend values mean the door is a branchmid?

    has_branch_NPT = False
    has_NPT_branch = False
    has_branch_PT = False
    has_PT_branch = False
    
    for path in room.paths:
        is_branch_NPT = branch_NPT(path)
        is_NPT_branch = NPT_branch(path)
        is_branch_PT = branch_PT(path)
        is_PT_branch = PT_branch(path)
        
        has_branch_NPT = has_branch_NPT or is_branch_NPT
        has_NPT_branch = has_NPT_branch or is_NPT_branch
        has_branch_PT = has_branch_PT or is_branch_PT
        has_PT_branch = has_PT_branch or is_PT_branch
    
    for door in room.doors:
        if (door.branchstart or door.branchend):
            return BranchType.MID
    
    if (has_branch_NPT and not has_NPT_branch) or (has_PT_branch and not has_branch_PT):
        return BranchType.START
    
    if (has_NPT_branch and not has_branch_NPT) or (has_branch_PT and not has_PT_branch):
        return BranchType.END
    
    if (has_branch_NPT and has_NPT_branch) or (has_branch_PT and has_PT_branch):
        return BranchType.ANY
    
    return BranchType.NONE

#branch_NPT = path starts at branch and is NPT
#NPT_branch = path ends at branch and is (NPT or [oneway and not PT])
#branch_PT = path start at branch is PT
#PT_branch = path end at branch is (PT or [oneway and not NPT])

#paths start at branch must be the correct time (IE not only oneway)
#otherwise nothing stops the player from doubling back the wrong way

def branch_NPT(path):
    return branch_TIME(path, PathTime.NOTPIZZATIME)

def NPT_branch(path):
    return TIME_branch(path, PathTime.NOTPIZZATIME, PathTime.PIZZATIME)

def branch_PT(path):
    return branch_TIME(path, PathTime.PIZZATIME)

def PT_branch(path):
    return TIME_branch(path, PathTime.PIZZATIME, PathTime.NOTPIZZATIME)

def branch_TIME(path, time):
    #return path.start_door.branch and path.path_time == time
    return path.start_door.branch and path.exit_door.exit_path_time == time

def TIME_branch(path, time, wrong_time):
    return path.exit_door.branch and (path.start_door.start_path_time == time or path.oneway) and path.start_door.start_path_time is not wrong_time

def get_room_type(room):
    if (room.has_john):
        return RoomType.JOHN
    
    if (room.has_entrance):
        return RoomType.ENTRANCE
    
    if (room.branch_type is not BranchType.NONE):
        return RoomType.BRANCH
    
    if (len(room.paths) == 1):
        return RoomType.LOOP
    
    return RoomType.NORMAL

def get_dir(j_door_dir):
    if j_door_dir is None:
        return DoorDir.NONE
    elif j_door_dir == "up":
        return DoorDir.UP
    elif j_door_dir == "down":
        return DoorDir.DOWN
    elif j_door_dir == "left":
        return DoorDir.LEFT
    elif j_door_dir == "right":
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
        return door_dir

def get_path_time(j_door):
    if (DOOR_PIZZATIME in j_door):
        return PathTime.PIZZATIME
    elif (DOOR_NOTPIZZATIME in j_door):
        return PathTime.NOTPIZZATIME
    else:
        return PathTime.BOTH

def get_door_type(j_door_type):
    if j_door_type is None:
        return DoorType.NONE
    elif j_door_type == "horizontal":
        return DoorType.HORIZONTAL
    elif j_door_type == "vertical":
        return DoorType.VERTICAL
    elif j_door_type == "door":
        return DoorType.DOOR
    elif j_door_type == "box":
        return DoorType.BOX
    elif j_door_type == "secret":
        return DoorType.SECRET
    elif j_door_type == "rocket":
        return DoorType.ROCKET
    elif j_door_type == "taxi":
        return DoorType.TAXI
    elif j_door_type == "leveldoor":
        return DoorType.LEVELDOOR
    else:
        return DoorType.ANY