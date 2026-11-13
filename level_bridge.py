#Author: Stack Man
#Date: 11/9/2026

#Bridge two rooms using the Flow Graph and select their rooms

from objects import Room
from colors import RESET, ERROR
from level_objects import TwowaySegment, BranchSegment, RoomSelection, RoomPath, BranchRoomPath, BaseRoomPath
from enums import PathTime, RoomType, DoorType, TraversalType
from pairs import pairs
from graph_from_rooms import FlowGraphHandler

from level_get_traversal import get_traversal
from level_select_rooms import select_rooms

LOG_FAILED_RP_PAIRS = True
LOG_FAILED_BRIDGE = True

def log_rp(msg: str|RuntimeError):
    if (LOG_FAILED_RP_PAIRS):
        print(msg)

def log_bridge(msg: str|RuntimeError):
    if (LOG_FAILED_BRIDGE):
        print(msg)



def bridge_twoway(start_rp: BaseRoomPath, end_rp: BaseRoomPath, FG: FlowGraphHandler):

    log_bridge(f"bridge_twoway: try bridge TW {start_rp} to {end_rp}")

    try:
        log_bridge(f"bridge_twoway: getting traversal")
        traversal = get_traversal(start_rp, end_rp, FG, TraversalType.ANY)
        log_bridge(f"   bridge_twoway: got traversal {traversal}")
        log_bridge(f"bridge_twoway: getting selection")
        room_selection = select_rooms(FG, traversal, TraversalType.ANY)
        log_bridge(f"   bridge_twoway: got selection {room_selection}")

        return TwowaySegment(start_rp, end_rp, room_selection)
    except RuntimeError as e:
        log_rp(e)

    raise RuntimeError(f"bridge_twoway: failed traversal or room_selection")

    
def bridge_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, FG: FlowGraphHandler):
    try:
        NPT = bridge_oneway_branch(start_rp, end_rp, TraversalType.NOTPIZZATIME, FG)
        PT = bridge_oneway_branch(end_rp, start_rp, TraversalType.PIZZATIME, FG)

        return BranchSegment(start_rp, end_rp, PT, NPT)
    except RuntimeError as e:
        log_rp(e)

    raise RuntimeError(f"bridge_twoway: failed traversal or room_selection")
    

def bridge_oneway_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, traversal_type: TraversalType, FG: FlowGraphHandler):
    traversal = get_traversal(start_rp, end_rp, FG, traversal_type)
    room_selection = select_rooms(FG, traversal, traversal_type)
    return room_selection

#Iterators that yield every potential combination of start path and end path for the selected SD
#catch errors on bridge failure
#utilize recursion to maintain position within iterator in case of step-back

def bridge_twoway_room_room(start_room: Room, end_room: Room, FG: FlowGraphHandler):
    log_rp(f"Try bridge_twoway_room_room between {start_room} and {end_room}")

    match start_room.room_type:
        case RoomType.ENTRANCE:
            return bridge_twoway_from_entrance(start_room, end_room, FG)
        case _:
            raise NotImplementedError(f"{ERROR}ERROR: bridge_twoway_room_room() not implemented for start_room of type {start_room.room_type}{RESET}")

    raise RuntimeError(f"Could not bridge_twoway_room_room between {start_room} and {end_room}")
    

def bridge_branch_room_room(start_room: Room, end_room: Room, FG: FlowGraphHandler):
    log_rp(f"Try bridge_branch_room_room between {start_room} and {end_room}")

    i = 0
    s = 0
    e = 0

    for start_rp in branch_room_path(start_room):
        s += 1
        for end_rp in branch_room_path(end_room):
            e += 1
            i += 1
            try:
                yield bridge_branch(start_rp, end_rp, FG)
            except RuntimeError as e:
                #failure is added within bridge_branch so that only the failed  PT/NPT pair isa dded
                log_rp(e)

    raise RuntimeError(f"Could not bridge_branch_room_room between {start_room} and {end_room} after {i} pairs, {s} srps with {e} erps")


def bridge_twoway_from_entrance(start_room: Room, end_room: Room, FG: FlowGraphHandler):
    for start_rp in entrance_room_path(start_room):
        for end_rp in room_path(end_room):
            try:
                yield bridge_twoway(start_rp, end_rp, FG)
            except RuntimeError as e:
                log_rp(e)

    raise RuntimeError("Could not bridge_twoway_from_entrance")

#make bridges from start room with already selected paths
def bridge_twoway_rp_room(start_rp: BaseRoomPath, end_room: Room, FG: FlowGraphHandler):
    for end_rp in room_path(end_room):
        try:
            yield bridge_twoway(start_rp, end_rp, FG)
        except RuntimeError as e:
            log_rp(e)

    raise RuntimeError("Could not bridge_twoway_rp_room")

def bridge_branch_rp_room(start_rp: BranchRoomPath, end_room: Room, FG: FlowGraphHandler):
    for end_rp in branch_room_path(end_room):
        #branch will connect NPT and PT together, so check both
        try:
            yield bridge_branch(start_rp, end_rp, FG)
        except RuntimeError as e:
            #failure is added within bridge_branch so that only the failed  PT/NPT pair isa dded
            log_rp(e)

    raise RuntimeError("Could not bridge_branch_rp_room")

#iterate over potential RoomPath candidates for a room type

def branch_room_path(room: Room):
    log_rp(f"branch_room_path: gen for {room.room_type} of {room}")

    try:
        match room.room_type: #entrance/john dont have an actual branch door
            case RoomType.ENTRANCE:
                log_rp(f"   branch_room_path: gen for ENTRANCE called")
                return entrance_branch_room_path(room)
            case RoomType.JOHN:
                log_rp(f"   branch_room_path: gen for JOHN called")
                return john_branch_room_path(room)
            case RoomType.BRANCH:
                log_rp(f"   branch_room_path: gen for BRANCH called")
                return branch_branch_room_path(room)
            case _:
                raise NotImplementedError(f"branch_room_path: not implemented for {room.room_type}")
    except RuntimeError as e:
        log_rp(e)

    raise RuntimeError(f"branch_room_path: could not get branch path from {room}")

def branch_branch_room_path(room: Room):
    i = 0

    for A, B in pairs(room.paths):
        i += 1
        if (A.start_door.branch and B.exit_door.branch):
            yield BranchRoomPath(room, A, B, A.start_door)
        elif (A.exit_door.branch and B.start_door.branch):
            yield BranchRoomPath(room, B, A, A.exit_door)

    raise RuntimeError(f"branch_branch_room_path: no valid path pair after {i} pairs")

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

def room_path(room: Room):
    match room.room_type:
        case RoomType.BRANCH:
            return branch_room_path(room)
        case RoomType.JOHN:
            return any_room_path(room)
        case _ :
            raise ValueError(f"{ERROR}ERROR: room_path() not implemented for room of type {room.room_type}")

def entrance_room_path(room: Room):
    for P in room.paths:
        if P.start_door.letter == "A" and P.start_door.door_type == DoorType.LEVELDOOR:
            yield RoomPath(room, P)

def any_room_path(room: Room):
    for P in room.paths:
        yield RoomPath(room, P)
        