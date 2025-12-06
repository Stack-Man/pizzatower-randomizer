from enums import *
from json_keys import *

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
    paths = doors_to_paths(doors, is_john_room)
    
    room = Room(room_name, doors, paths)
    
    branch_type = get_branch_type(room)
    room_type = get_room_type(room, branch_type)
    
    room.branch_type = branch_type
    room.room_type = room_type
    
    return room
    
    
def json_to_doors(json_room):
    if JSON_DOORS not in json_room:
        return []
    
    doors = []
    
    for json_door in json_doors:
        door = json_to_door(json_door)
        doors.append(door)

    return doors

def json_to_door(json_door):
    
    letter = json_door.get(DOOR_LETTER)
    door_type = json_door.get(DOOR_TYPE)
    door_dir = json_door.get(DOOR_DIR)

    if door_dir == None:
        door_dir = DoorDir.NONE

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
    path_time_if_start = PathTime.BOTH

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

def doors_to_path(start_door, exit_door, is_john_room)

    #start is exitonly or exit is startonly
    if start_door.access_type == AccessType.EXITONLY or exit_door.access_type == AccessType.STARTONLY:
        return None

    #path time mismatch, unless it is in a john room
    #path times of start and exit must match or at least one is BOTH
    if not is_john_room and (start_door.start_path_time is not PathTime.BOTH or exit_door.exit_path_time is not PathTime.BOTH) and start_door.start_path_time is not exit_door.exit_path_time:
        return None
    
    #Determine which path_time to set the path
    path_time = PathTime.BOTH

    if not is_john_room:
        if start_door.start_path_time == PathTime.PIZZATIME or exit_door.exit_path_time == PathTime.PIZZATIME:
            path_time = PathTime.PIZZATIME
        
        if start_door.start_path_time == PathTime.NOTPIZZATIME or exit_door.exit_path_time == PathTime.NOTPIZZATIME:
            path_time = PathTime.NOTPIZZATIME
    
    #oneway = start or exit only but not initially blocked
    is_oneway = (start_door.access_type == AccessType.STARTONLY and not start_door.initially_blocked) or (exit_door.access_type == AccessType.EXITONLY and not exit_door.initially_blocked)
    
    is_loop = start_door.is_loop or exit_door.is_loop

    path = Path(start_door, exit_door, path_time, is_oneway, is_loop)

    return path

#-------------------
#   Object Helpers
#-------------------
def get_branch_type(room):
    #Check for doors that contain "branch"
    #TODO: figure out what branchstart and branchend values mean
    
    #get paths that start or end on the branch door and dont include "loop"
    
    
    return None #TODO
    
"""
function rd_check_paths_for_branchtype(path_ab, path_ba, current_type)
{	
	if ((path_ab != undefined && !path_ab.startdoor.branch && !path_ab.exitdoor.branch)
	||  (path_ba != undefined && !path_ba.startdoor.branch && !path_ba.exitdoor.branch))
	{
		return current_type; //branch check failed
	}
	
	//path == undefined means the other is a oneway
	//to branch path (ba) being oneway is a valid alternative to being notpizzatime/pizzatime exclusive
	
	//Check both in case branch is a or b
	var branch_NPT = rd_branch_NPT(path_ab) || rd_branch_NPT(path_ba);
	var NPT_branch = rd_NPT_branch(path_ab) || rd_NPT_branch(path_ba);
	
	var branch_PT = rd_branch_PT(path_ab) || rd_branch_PT(path_ba);
	var PT_branch = rd_PT_branch(path_ab) || rd_PT_branch(path_ba);
	
	if ( (branch_NPT && ! NPT_branch) || (!branch_PT && PT_branch) )
		return roomtype.branchstart;
	
	if ( (NPT_branch && ! branch_NPT) || (!PT_branch && branch_PT) )
		return roomtype.branchend;
	
	if ( (branch_NPT && NPT_branch) || (branch_PT && PT_branch) )
		return roomtype.branchany;
	
	return current_type; //branch check failed
}

function rd_branch_NPT(path)
{
	return (path != undefined) && path.startdoor.branch && path.pathtime == pathtime.notpizzatime;
}

function rd_NPT_branch(path)
{
	return (path != undefined) && (path.pathtime == pathtime.notpizzatime || path.oneway) && path.pathtime != pathtime.pizzatime && path.exitdoor.branch;
}

function rd_branch_PT(path)
{
	return (path != undefined) && path.startdoor.branch && path.pathtime == pathtime.pizzatime;
}

function rd_PT_branch(path)
{
	return (path != undefined) && (path.pathtime == pathtime.pizzatime || path.oneway) && path.pathtime != pathtime.notpizzatime  && path.exitdoor.branch;
}


function rd_check_all_paths_for_special_branch(paths, has_pillar, has_entrance, current_type)
{
	var has_pizzatime = false;
	var has_notpizzatime = false;
	
	var has_branchstart = false;
	
	for (var p = 0; p < ds_list_size(paths); p++)
	{
		var path = ds_list_find_value(paths, p);
		
		//TODO: may be redundant with the below check
		if (path.pathtime == pathtime.pizzatime)
			has_pizzatime = true;
		else if (path.pathtime == pathtime.notpizzatime)
			has_notpizzatime = true;
		
		//Accounts for john branching paths as well which are marked as pathtime.any
		if (path.startdoor.pizzatime || path.exitdoor.pizzatime)
			has_pizzatime = true;
		
		if (path.startdoor.notpizzatime || path.exitdoor.notpizzatime)
			has_notpizzatime = true;
		
		if (has_pizzatime && has_notpizzatime)
		{
			if (has_pillar)
				return roomtype.johnbranching;
				
			if (has_entrance)
				return roomtype.entrancebranching;
		}
		
		if (path.startdoor.branchstart)
			return roomtype.branchmid;
	}
	
	if (has_pillar)
		return roomtype.john;
	
	if (has_entrance)
		return roomtype.entrance;
	
	return current_type; //check failed
}
"""

def get_room_type(room):
    return None #TODO

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

        