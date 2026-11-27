#Author Stack Man
#Date: 11/13/2026

#Take a room and generate all valid room and path combinations
#that a specific bridge might want

#iterate over potential RoomPath candidates for a room type

from json_objects import Room, Path
from enums import StartExitType, RoomType, PathTime, DoorType, TraversalType
from pairs import pairs
from level_objects import BranchRoomPath, RoomPath
from colors import ERROR, RESET

import logging as log

#for generators, avoid raising error on generation exhausation
#as the calling loop needs to continue cleanly

def branch_room_path(room: Room, se_type: StartExitType):
    #log_rp(f"branch_room_path: gen for {room.room_type} of {room}")

    try:
        match room.room_type: #entrance/john dont have an actual branch door
            case RoomType.ENTRANCE:
                #log_rp(f"   branch_room_path: gen for ENTRANCE called")
                return entrance_branch_room_path(room)
            case RoomType.JOHN:
                #log_rp(f"   branch_room_path: gen for JOHN called")
                return john_branch_room_path(room)
            case RoomType.BRANCH:
                #log_rp(f"   branch_room_path: gen for BRANCH called")
                return branch_branch_room_path(room, se_type)
            case _:
                raise NotImplementedError(f"branch_room_path: not implemented for {room.room_type}")
    except RuntimeError as e:
        pass

    #this should never happen
    raise NotImplementedError(f"{ERROR}branch_room_path: could not get branch path from {room} This line should never run!{RESET}")

def branch_branch_room_path(room: Room, se_type: StartExitType):   
    debug = False

    for A, B in pairs(room.paths):
        #branch is source
        #we want branch > NPT and PT > branch

        if (A == B):
            log.debug("A is B in branch branch room path %s and %s", A, B)

        if (se_type == StartExitType.START):

            if branch_NPT_and_PT_branch(A, B):
                yield BranchRoomPath(room, A, B, A.start_door)
            elif branch_NPT_and_PT_branch(B, A):
                yield BranchRoomPath(room, B, A, B.start_door)

        #branch is destination
        #we want NPT > branch and branch > PT
        else:

            if NPT_branch_and_branch_PT(A, B):
                yield BranchRoomPath(room, A, B, A.exit_door)
            elif NPT_branch_and_branch_PT(B, A):
                yield BranchRoomPath(room, B, A, B.exit_door)

def branch_NPT_and_PT_branch(A: Path, B: Path):
    #dont allow taking reverse of self as branch path, for dual branch door rooms
    if (A.exit_door == B.start_door):
        return False
    
    if (A.start_door.branch and A.get_path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]):
        if (B.exit_door.branch and B.get_path_time() in [PathTime.PIZZATIME, PathTime.BOTH]):
            if (A.start_door.letter == B.exit_door.letter): #also check that the branch doors are the same, in case of multiple branch doors in room
                return True

    return False

def NPT_branch_and_branch_PT(A: Path, B: Path):
    #dont allow taking reverse of self as branch path, for dual branch door roomsm the shared door can only be A.xit and B.start
    if (A.start_door == B.exit_door): 
        return False
    
    if (A.exit_door.branch and A.get_path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]):
        if (B.start_door.branch and B.get_path_time() in [PathTime.PIZZATIME, PathTime.BOTH]):
            if (A.exit_door.letter == B.start_door.letter):
                return True

    return False

def entrance_branch_room_path(room: Room):
    for A, B in pairs(room.paths):
        #NPT must start with leveldoor and PT must end with leveldoor

        if (LDNPT_to_PTLD(A, B)):
            yield BranchRoomPath(room, A, B, A.start_door)
        elif(LDNPT_to_PTLD(B, A)):
            yield BranchRoomPath(room, B, A, B.start_door)
        else:
            pass

def LDNPT_to_PTLD(A: Path, B: Path):
    if (A.start_door.door_type == DoorType.LEVELDOOR and A.get_path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]):
        if (B.exit_door.door_type == DoorType.LEVELDOOR and B.get_path_time() in [PathTime.PIZZATIME, PathTime.BOTH]):
            return True
    
    return False

def john_branch_room_path(room: Room):
    for P in room.paths:
        if (P.start_door.start_path_time == PathTime.NOTPIZZATIME and P.exit_door.exit_path_time == PathTime.PIZZATIME):
            #will use NPT's start and PT's exit, so its already lined up
            #the branch door will not be used since its a john room
            yield BranchRoomPath(room, P, P, P.start_door)

def room_path_cap_TW(room: Room):
    match room.room_type:
        case RoomType.BRANCH:
            #capping a TW, we enter from branch door
            #so branch type is start
            return branch_room_path(room, StartExitType.START) 
        case RoomType.JOHN:
            return any_room_path(room)
        case _ :
            raise ValueError(f"{ERROR}ERROR: room_path() not implemented for room of type {room.room_type}{RESET}")

def entrance_room_path(room: Room):
    for P in room.paths:
        if P.start_door.letter == "A" and P.start_door.door_type == DoorType.LEVELDOOR:
            yield RoomPath(room, P)

def any_room_path(room: Room):
    for P in room.paths:
        yield RoomPath(room, P)

def oneway_entrance_room_path(room: Room, traversal_type: TraversalType):
    for P in room.paths:
        if P.start_door.letter == "A" and P.start_door.door_type == DoorType.LEVELDOOR:
            
            path_times = get_times(traversal_type)

            if P.get_path_time() in path_times:
                yield RoomPath(room, P)
                    
    
def oneway_exit_room_path(room: Room, traversal_type: TraversalType):
    for P in room.paths:

        if P.exit_door.letter == "A" and P.exit_door.door_type == DoorType.LEVELDOOR:

            path_times = get_times(traversal_type)

            if P.get_path_time() in path_times:
                yield RoomPath(room, P)

def get_times(traversal_type: TraversalType):
    match traversal_type:
        case TraversalType.NOTPIZZATIME:
            return [PathTime.NOTPIZZATIME, PathTime.BOTH]
        case TraversalType.PIZZATIME:
            return [PathTime.PIZZATIME, PathTime.BOTH]
        case _:
            raise NotImplementedError("%soneway_entrance_room_path not implemented for traversal type %s%s", ERROR, traversal_type, RESET)