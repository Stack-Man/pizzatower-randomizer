#Author Stack Man
#Date: 11/13/2026

#Take a room and generate all valid room and path combinations
#that a specific bridge might want

#iterate over potential RoomPath candidates for a room type

from objects import Room, Path
from enums import StartExitType, RoomType, PathTime, DoorType
from pairs import pairs
from level_objects import BranchRoomPath, RoomPath
from colors import ERROR, RESET

LOG_FAILED_RP_PAIRS = True
LOG_NPTPTB_CHECK = False

def log_rp(msg: str|RuntimeError):
    if (LOG_FAILED_RP_PAIRS):
        print(msg)


def log_nptb(msg: str|RuntimeError):
    if (LOG_NPTPTB_CHECK):
        print(msg)

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

    raise RuntimeError(f"branch_room_path: could not get branch path from {room}")

def branch_branch_room_path(room: Room, se_type: StartExitType):
    i = 0

    log_nptb(f"branch_branch_room_path: {room} as {se_type}")

    for A, B in pairs(room.paths):
        i += 1

        #branch is source
        #we want branch > NPT and PT > branch
        
        

        if (se_type == StartExitType.START):

            if branch_NPT_and_PT_branch(A, B):
                yield BranchRoomPath(room, A, B, A.start_door)
            elif branch_NPT_and_PT_branch(B, A):
                yield BranchRoomPath(room, B, A, B.start_door)
            else:
                log_nptb(f"           {A}, {B} not BNPT to PTB or PTB to BNPT")
            

        #branch is destination
        #we want NPT > branch and branch > PT
        else:

            if NPT_branch_and_branch_PT(A, B):
                yield BranchRoomPath(room, A, B, A.exit_door)
            elif NPT_branch_and_branch_PT(B, A):
                yield BranchRoomPath(room, B, A, B.exit_door)
            else:
                log_nptb(f"           {A}, {B} not NPTB to BPT or BPT to NPTB")

    raise RuntimeError(f"branch_branch_room_path: no valid path pair after {i} pairs")

def branch_NPT_and_PT_branch(A: Path, B: Path):
    log_nptb(f"{A} is Branch NPT and {B} is PT Branch?")
    
    if (A.start_door.branch and A.path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]):
        if (B.exit_door.branch and B.path_time() in [PathTime.PIZZATIME, PathTime.BOTH]):
            log_nptb(f"       pass")
            return True
        else:
            log_nptb(f"       {A} start not branch: {A.start_door.branch} or {A.path_time()} not PT/BOTH")
            return False
    else:
        log_nptb(f"       {A} start not branch: {A.start_door.branch} or {A.path_time()} not NPT/BOTH")
        return False

def NPT_branch_and_branch_PT(A: Path, B: Path):
    if (A.exit_door.branch and A.path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]):
        if (B.start_door.branch and B.path_time() in [PathTime.PIZZATIME, PathTime.BOTH]):
            return True

    return False

def entrance_branch_room_path(room: Room):
    log_rp(f"entrance_branch_room_path: try {room}")

    i = 0

    for A, B in pairs(room.paths):
        i += 1

        A_NPT = A.path_time == PathTime.NOTPIZZATIME or A.path_time == PathTime.BOTH
        A_start_leveldoor = A.start_door.door_type == DoorType.LEVELDOOR
        B_PT = B.path_time == PathTime.PIZZATIME or B.path_time == PathTime.BOTH
        B_end_leveldoor = B.exit_door.door_type == DoorType.LEVELDOOR

        #NPT must start with leveldoor and PT must end with leveldoor

        if (A_NPT and A_start_leveldoor and B_PT and B_end_leveldoor):
            yield BranchRoomPath(room, A, B, A.start_door)
        else:
            B_NPT = B.path_time == PathTime.NOTPIZZATIME or B.path_time == PathTime.BOTH
            B_start_leveldoor = B.start_door.door_type == DoorType.LEVELDOOR
            A_PT = A.path_time == PathTime.PIZZATIME or A.path_time == PathTime.BOTH
            A_end_leveldoor = A.exit_door.door_type == DoorType.LEVELDOOR

            if (B_NPT and B_start_leveldoor and A_PT and A_end_leveldoor):
                yield BranchRoomPath(room, B, A, B.start_door)
            else:
                pass
                #log_rp(f"invalid path pair of {A} and {B}")
                #A.print_stats_extended()
                #B.print_stats_extended()

    raise RuntimeError(f"entrance_branch_room_path: no valid path pair after {i} pairs")

def john_branch_room_path(room: Room):
    i = 0

    for P in room.paths:
        i += 1
        if (P.start_door.start_path_time == PathTime.NOTPIZZATIME and P.exit_door.exit_path_time == PathTime.PIZZATIME):

            #will use NPT's start and PT's exit, so its already lined up
            #the branch door will not be used since its a john room
            yield BranchRoomPath(room, P, P, P.start_door)

    raise NotImplementedError(f"john_branch_room_path: no valid path after {i} paths")

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