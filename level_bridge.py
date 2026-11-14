#Author: Stack Man
#Date: 11/9/2026

#Bridge two rooms using the Flow Graph and select their rooms

from objects import Room
from colors import RESET, ERROR
from level_objects import TwowaySegment, BranchSegment, BranchRoomPath, BaseRoomPath
from enums import RoomType, TraversalType, StartExitType
from graph_from_rooms import FlowGraphHandler

from level_get_traversal import get_traversal
from level_select_rooms import select_rooms


from level_room_path_generator import branch_room_path, room_path_cap_TW, entrance_room_path

LOG_FAILED_BRIDGE = True



def log_bridge(msg: str|RuntimeError):
    if (LOG_FAILED_BRIDGE):
        print(msg)

#Main Bridge functions that take a Source and Destination 
#with their selected paths and creates a LevelSegment from it

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
        log_bridge(e)

    raise RuntimeError(f"bridge_twoway: failed traversal or room_selection")

    
def bridge_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, FG: FlowGraphHandler):
    try:
        NPT = bridge_oneway_branch(start_rp, end_rp, TraversalType.NOTPIZZATIME, FG)
        PT = bridge_oneway_branch(end_rp, start_rp, TraversalType.PIZZATIME, FG)

        return BranchSegment(start_rp, end_rp, PT, NPT)
    except RuntimeError as e:
        log_bridge(e)

    raise RuntimeError(f"bridge_twoway: failed traversal or room_selection")
    

def bridge_oneway_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, traversal_type: TraversalType, FG: FlowGraphHandler):
    traversal = get_traversal(start_rp, end_rp, FG, traversal_type)
    room_selection = select_rooms(FG, traversal, traversal_type)
    return room_selection

#Iterators that yield every potential combination of start path and end path for the selected SD
#catch errors on bridge failure
#utilize recursion to maintain position within iterator in case of step-back

def bridge_twoway_room_room(start_room: Room, end_room: Room, FG: FlowGraphHandler):
    log_bridge(f"Try bridge_twoway_room_room between {start_room} and {end_room}")

    match start_room.room_type:
        case RoomType.ENTRANCE:
            return bridge_twoway_from_entrance(start_room, end_room, FG)
        case _:
            raise NotImplementedError(f"{ERROR}ERROR: bridge_twoway_room_room() not implemented for start_room of type {start_room.room_type}{RESET}")

    raise RuntimeError(f"Could not bridge_twoway_room_room between {start_room} and {end_room}")
    

def bridge_branch_room_room(start_room: Room, end_room: Room, FG: FlowGraphHandler):
    log_bridge(f"Try bridge_branch_room_room between {start_room} and {end_room}")

    i = 0
    s = 0
    e = 0

    #branch to branch, connecting BS/BA to BE/BA 
    for start_rp in branch_room_path(start_room, StartExitType.START): #branch is source
        s += 1
        for end_rp in branch_room_path(end_room, StartExitType.EXIT): #branch is destination
            e += 1
            i += 1
            try:
                yield bridge_branch(start_rp, end_rp, FG)
            except RuntimeError as e:
                #failure is added within bridge_branch so that only the failed  PT/NPT pair isa dded
                log_bridge(e)

    raise RuntimeError(f"Could not bridge_branch_room_room between {start_room} and {end_room} after {i} pairs, {s} srps with {e} erps")


def bridge_twoway_from_entrance(start_room: Room, end_room: Room, FG: FlowGraphHandler):
    for start_rp in entrance_room_path(start_room):
        for end_rp in room_path_cap_TW(end_room):
            try:
                yield bridge_twoway(start_rp, end_rp, FG)
            except RuntimeError as e:
                log_bridge(e)

    raise RuntimeError("Could not bridge_twoway_from_entrance")

#make bridges from start room with already selected paths
def bridge_twoway_rp_room(start_rp: BaseRoomPath, end_room: Room, FG: FlowGraphHandler):
    for end_rp in room_path_cap_TW(end_room):
        try:
            yield bridge_twoway(start_rp, end_rp, FG)
        except RuntimeError as e:
            log_bridge(e)

    raise RuntimeError("Could not bridge_twoway_rp_room")

def bridge_branch_rp_room(start_rp: BranchRoomPath, end_room: Room, FG: FlowGraphHandler):

    #srp is BS/BA so end_rp is BE/BA
    for end_rp in branch_room_path(end_room, StartExitType.EXIT):
        #branch will connect NPT and PT together, so check both
        try:
            yield bridge_branch(start_rp, end_rp, FG)
        except RuntimeError as e:
            #failure is added within bridge_branch so that only the failed  PT/NPT pair isa dded
            log_bridge(e)

    raise RuntimeError("Could not bridge_branch_rp_room")


        