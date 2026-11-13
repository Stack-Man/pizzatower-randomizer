#Author: Stack Man
#Date: 11/9/2026

#Bridge two rooms using the Flow Graph and select their rooms

from objects import Room
from colors import RESET, ERROR
from level_objects import TwowaySegment, BranchSegment, RoomSelection, RoomPath, BranchRoomPath, BaseRoomPath
from enums import PathTime, RoomType, DoorType, TraversalType
from pairs import pairs
from graph_from_rooms import FlowGraphHandler

import networkx as nx

from level_get_traversal import get_traversal
from level_select_rooms import select_rooms

LOG_FAILED_RP_PAIRS = True
LOG_FAILED_BRIDGE = True

def log_rp(msg: str|Exception):
    if (LOG_FAILED_RP_PAIRS):
        print(msg)

def log_bridge(msg: str|Exception):
    if (LOG_FAILED_BRIDGE):
        print(msg)



def bridge_twoway(start_rp: BaseRoomPath, end_rp: BaseRoomPath, FG: FlowGraphHandler):

    log_rp(f"try bridge TW {start_rp} to {end_rp}")

    try:
        traversal = get_traversal(start_rp, end_rp, FG, TraversalType.ANY)
        room_selection = select_rooms(FG, traversal, TraversalType.ANY)
    except Exception as e:
        log_rp(e)

    return TwowaySegment(start_rp, end_rp, room_selection)

def bridge_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, FG: FlowGraphHandler):
    try:
        NPT = bridge_oneway_branch(start_rp, end_rp, TraversalType.NOTPIZZATIME, FG)
        PT = bridge_oneway_branch(end_rp, start_rp, TraversalType.PIZZATIME, FG)
    except Exception as e:
        log_rp(e)

    return BranchSegment(start_rp, end_rp, PT, NPT)
    

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

    for start_rp in branch_room_path(start_room):
        for end_rp in branch_room_path(end_room):
            try:
                yield bridge_branch(start_rp, end_rp, FG)
            except Exception as e:
                #failure is added within bridge_branch so that only the failed  PT/NPT pair isa dded
                log_rp(e)

    start_room.print_stats()
    end_room.print_stats()

    raise RuntimeError(f"Could not bridge_branch_room_room between {start_room} and {end_room}")


def bridge_twoway_from_entrance(start_room: Room, end_room: Room, FG: FlowGraphHandler):
    for start_rp in entrance_room_path(start_room):
        for end_rp in room_path(end_room):
            try:
                yield bridge_twoway(start_rp, end_rp, FG)
            except Exception as e:
                log_rp(e)

    raise RuntimeError("Could not bridge_twoway_from_entrance")

#make bridges from start room with already selected paths
def bridge_twoway_rp_room(start_rp: BaseRoomPath, end_room: Room, FG: FlowGraphHandler):
    for end_rp in room_path(end_room):
        try:
            yield bridge_twoway(start_rp, end_rp, FG)
        except Exception as e:
            log_rp(e)

    raise RuntimeError("Could not bridge_twoway_rp_room")

def bridge_branch_rp_room(start_rp: BranchRoomPath, end_room: Room, FG: FlowGraphHandler):
    for end_rp in branch_room_path(end_room):
        #branch will connect NPT and PT together, so check both
        try:
            yield bridge_branch(start_rp, end_rp, FG)
        except Exception as e:
            #failure is added within bridge_branch so that only the failed  PT/NPT pair isa dded
            log_rp(e)

    raise RuntimeError("Could not bridge_branch_rp_room")

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
        