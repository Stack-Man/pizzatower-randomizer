#Author Stack Man
#Date: 11/13/2026

#Take a room and generate all valid room and path combinations
#that a specific bridge might want

#iterate over potential RoomPath candidates for a room type

from json_objects import Room, Path
from enums import StartExitType, RoomType, PathTime, DoorType
from pairs import pairs
from level_objects import BranchRoomPath, RoomPath
from colors import ERROR, RESET

LOG_FAILED_RP_PAIRS = True
LOG_NPTPTB_CHECK = True
LOG_LD_CHECK = True

def log_rp(msg: str|RuntimeError):
    if (LOG_FAILED_RP_PAIRS):
        print("             ROOM PATH: " + str(msg))


def log_nptb(msg: str|RuntimeError):
    if (LOG_NPTPTB_CHECK):
        print("             NPTB: " + str(msg))

def log_LD(msg: str|RuntimeError):
    if (LOG_LD_CHECK):
        print("         LD: " + str(msg))

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
        log_rp(e)

    #this should never happen
    raise NotImplementedError(f"{ERROR}branch_room_path: could not get branch path from {room} This line should never run!{RESET}")

def branch_branch_room_path(room: Room, se_type: StartExitType):

    debug = False

    if (room.name == "graveyard_3"):
        log_rp(f"{ERROR}BEGIN DEBUG graveyard_3{RESET}")
    
    i = 0
    s = 0

    log_nptb(f"branch_branch_room_path: {room} as {se_type}")

    for A, B in pairs(room.paths):
        i += 1

        #branch is source
        #we want branch > NPT and PT > branch
        
        

        if (se_type == StartExitType.START):

            if branch_NPT_and_PT_branch(A, B):
                s += 1
                yield BranchRoomPath(room, A, B, A.start_door)
            elif branch_NPT_and_PT_branch(B, A):
                s += 1
                yield BranchRoomPath(room, B, A, B.start_door)
            else:
                log_nptb(f"           {A}, {B} not BNPT to PTB or PTB to BNPT")
            

        #branch is destination
        #we want NPT > branch and branch > PT
        else:

            if NPT_branch_and_branch_PT(A, B):
                s += 1
                yield BranchRoomPath(room, A, B, A.exit_door)
            elif NPT_branch_and_branch_PT(B, A):
                s += 1
                yield BranchRoomPath(room, B, A, B.exit_door)
            else:
                log_nptb(f"           {A}, {B} not NPTB to BPT or BPT to NPTB")

    log_rp(f"branch_branch_room_path: {room} exhausted {i} pairs after {s} yields ")

def branch_NPT_and_PT_branch(A: Path, B: Path):
    log_nptb(f"CHECK: {A} is Branch NPT and {B} is PT Branch?")
    if (A.exit_door == B.start_door): #dont allow taking reverse of self as branch path, for dual branch door rooms
        log_nptb(f"     Fail, {A} exit = {B} start but must be different")
        return False
    
    if (A.start_door.branch and A.get_path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]):

        log_nptb(f"     A: {A} passes")
        
        if (B.exit_door.branch and B.get_path_time() in [PathTime.PIZZATIME, PathTime.BOTH]):
            log_nptb(f"     B: {B} passes")
            
            if (A.start_door.letter == B.exit_door.letter): #also check that the branch doors are the same, in case of multiple branch doors in room
                log_nptb(f"     branch same, total pass")
                return True
            else:
                log_nptb(f"     branch NOT same, Failed")
                return False
        else:
            log_nptb(f"     B: {B} Failed")
            return False
    else:
        log_nptb(f"     A: {A} Failed")
        return False

def NPT_branch_and_branch_PT(A: Path, B: Path):
    log_nptb(f"CHECK: {A} is NPT Branch and {B} is Branch PT?")
    
    if (A.start_door == B.exit_door): #dont allow taking reverse of self as branch path, for dual branch door roomsm the shared door can only be A.xit and B.start
        log_nptb(f"     Fail, {A} start = {B} exit but must be different")
        return False
    
    if (A.exit_door.branch and A.get_path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]):
        log_nptb(f"     A: {A} pass")
        if (B.start_door.branch and B.get_path_time() in [PathTime.PIZZATIME, PathTime.BOTH]):
            log_nptb(f"     B: {B} pass")
            if (A.exit_door.letter == B.start_door.letter):
                log_nptb(f"     AB share branch, total pass")
                return True
            else:
                log_nptb(f"     AB DONT share branch, Failed")
        else:
            log_nptb(f"     B: {B} Failed")
    else:
        log_nptb(f"     A: {A} Failed")

    return False

def entrance_branch_room_path(room: Room):
    log_rp(f"entrance_branch_room_path: try {room}")

    i = 0
    s = 0

    for A, B in pairs(room.paths):
        i += 1

        #NPT must start with leveldoor and PT must end with leveldoor

        if (LDNPT_to_PTLD(A, B)):
            log_rp(f"{room}: VALID path pair of {A} and {B}")
            s += 1
            yield BranchRoomPath(room, A, B, A.start_door)
        elif(LDNPT_to_PTLD(B, A)):
            log_rp(f"{room}: VALID path pair of {B} and {A}")
            s += 1
            yield BranchRoomPath(room, B, A, B.start_door)
        else:
            pass
            #log_rp(f"{room}: INVALID path pair of {A} and {B}")
            #A.print_stats_extended()
            #B.print_stats_extended()

    log_rp(f"entrance_branch_room_path: exhausted {i} pairs after {s} yields")

def LDNPT_to_PTLD(A: Path, B: Path):

    if (A.start_door.door_type == DoorType.LEVELDOOR and A.get_path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]):
        if (B.exit_door.door_type == DoorType.LEVELDOOR and B.get_path_time() in [PathTime.PIZZATIME, PathTime.BOTH]):
            return True
    
    return False

def john_branch_room_path(room: Room):
    i = 0
    y = 0

    for P in room.paths:
        i += 1
        if (P.start_door.start_path_time == PathTime.NOTPIZZATIME and P.exit_door.exit_path_time == PathTime.PIZZATIME):

            y += 1

            #will use NPT's start and PT's exit, so its already lined up
            #the branch door will not be used since its a john room
            yield BranchRoomPath(room, P, P, P.start_door)

    #keep as not implemented because this should never happen
    if (y <= 0):
        raise NotImplementedError(f"ERROR: john_branch_room_path: exhausted {i} paths but should have at least one valid")

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