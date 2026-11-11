#Author: Stack Man
#Date: 11/9/2026

#Bridge two rooms using the Flow Graph and select their rooms

from objects import Room, Door, Path
from colors import WARNING, RESET, ERROR
from level_objects import TwowaySegment, BranchSegment, RoomSelection, RoomPath, BranchRoomPath, BaseRoomPath

from enums import PathTime, RoomType, DoorType

from graph_collapse import pairs

from level_sd_memory_set import *

LOG_FAILED_RP_PAIRS = True

def log_rp(msg: str|Exception):
    if (LOG_FAILED_RP_PAIRS):
        print(msg)

def bridge_twoway(start_rp: BaseRoomPath, end_rp: BaseRoomPath, FG):

    #raise NotImplementedError(f"{ERROR}bridge_twoway() not implemented in level_bridge.py{RESET}")

    #1. take end type of start rp and start type of end rp
    #2. take any TR traversal from FG that matches and whose edges are > 0
    #3. select the rooms to fill the edges (avoiding an impossible booking using the bipartite graphs, if applicable)
    #4. decrease count of edges based on rooms selected

    return TwowaySegment(start_rp, end_rp, RoomSelection([]))

def bridge_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, FG):
    #raise NotImplementedError(f"{ERROR}bridge_branch() not implemented in level_bridge.py{RESET}")

    NPT = None
    PT = None

    #individual try catch so we can correctly attribute SD failure to the correct time
    try:
        NPT = bridge_oneway_branch(start_rp, end_rp, PathTime.NOTPIZZATIME, FG)
    except Exception as e:
        raise(e) #pass the exception to the calling function

    try:
        PT = bridge_oneway_branch(end_rp, start_rp, PathTime.PIZZATIME, FG)
    except Exception as e:
        raise(e)

    return BranchSegment(start_rp, end_rp, PT, NPT)

def bridge_oneway_branch(start_room: BranchRoomPath, end_room: BranchRoomPath, path_time: PathTime, FG):
    #raise NotImplementedError(f"{ERROR}bridge_oneway_branch() not implemented in level_bridge.py{RESET}")
    
    return RoomSelection([])

#Iterators that yield every potential combination of start path and end path for the selected SD
#catch errors on bridge failure
#utilize recursion to maintain position within iterator in case of step-back

def bridge_twoway_room_room(start_room: Room, end_room: Room, FG):
    match start_room.room_type:
        case RoomType.ENTRANCE:
            return bridge_twoway_from_entrance(start_room, end_room, FG)
        case _:
            raise NotImplementedError(f"{ERROR}ERROR: bridge_twoway_room_room() not implemented for start_room of type {start_room.room_type}{RESET}")
    

def bridge_branch_room_room(start_room: Room, end_room: Room, FG):
    for start_rp in branch_room_path(start_room):
        for end_rp in branch_room_path(end_room):
            try:
                yield bridge_branch(start_rp, end_rp, FG)
            except Exception as e:
                #failure is added within bridge_branch so that only the failed  PT/NPT pair isa dded
                log_rp(e)


def bridge_twoway_from_entrance(start_room: Room, end_room: Room, FG):
    for start_rp in entrance_room_path(start_room):
        for end_rp in room_path(end_room):
            try:
                yield bridge_twoway(start_rp, end_rp, FG)
            except Exception as e:
                log_rp(e)

#make bridges from start room with already selected paths
def bridge_twoway_rp_room(start_rp: BaseRoomPath, end_room: Room, FG):
    for end_rp in room_path(end_room):
        try:
            yield bridge_twoway(start_rp, end_rp, FG)
        except Exception as e:
            log_rp(e)

def bridge_branch_rp_room(start_rp: BranchRoomPath, end_room: Room, FG):
    for end_rp in branch_room_path(end_room):
        #branch will connect NPT and PT together, so check both
        try:
            yield bridge_branch(start_rp, end_rp, FG)
        except Exception as e:
            #failure is added within bridge_branch so that only the failed  PT/NPT pair isa dded
            log_rp(e)


#iterate over potential RoomPath candidates for a room type

def branch_room_path(room: Room):
    for A, B in pairs(room.paths):
        if (A.start_door.branch and B.exit_door.branch):
            yield BranchRoomPath(room, A, B, A.start_door)
        elif (A.exit_door.branch and B.start_door.branch):
            yield BranchRoomPath(room, B, A, A.exit_door)

def room_path(room: Room):
    match room.room_type:
        case RoomType.BRANCH:
            return branch_room_path(room)
        case _ :
            raise ValueError(f"{ERROR}ERROR: room_path() not implemented for room of type {room.room_type}")

def entrance_room_path(room: Room):
    for P in room.paths:
        if P.start_door.letter == "A" and P.start_door.door_type == DoorType.LEVELDOOR:
            yield RoomPath(room, P)
        