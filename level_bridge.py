#Author: Stack Man
#Date: 11/9/2026

#Bridge two rooms using the Flow Graph and select their rooms

from json_objects import Room, SelfLoop
from level_objects import TwowaySegment, BranchSegment, BranchRoomPath, BaseRoomPath, RoomPath
from enums import RoomType, TraversalType, StartExitType, PathTime
from graph_from_rooms import FlowGraphHandler

from level_get_traversal import get_traversal
from level_select_rooms import select_rooms
from level_room_path_generator import branch_room_path, room_path_cap_TW, entrance_room_path

from colors import RESET, ERROR

#Main Bridge functions that take a Source and Destination 
#with their selected paths and creates a LevelSegment from it

def bridge_twoway(start_rp: BaseRoomPath, end_rp: BaseRoomPath, FG: FlowGraphHandler):
    #need to preverse pre-bridge FG
    #in case we consume a room but ultimately fail
    pre_bridge_FG = FG.copy()

    try:
        
        traversal = get_traversal(start_rp, end_rp, FG, TraversalType.ANY)
        room_selection = select_rooms(FG, traversal, TraversalType.ANY)
        return TwowaySegment(start_rp, end_rp, room_selection)
    
    except RuntimeError as e:
        pass

    #on fail, revert FG so that selected rooms/traversals
    #are replenished
    FG.revert(pre_bridge_FG) 
    raise RuntimeError(f"bridge_twoway: failed traversal or room_selection between {start_rp.room} and {end_rp.room}")

    
def bridge_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, FG: FlowGraphHandler):
    pre_bridge_FG = FG.copy()

    try:
    
        NPT = bridge_oneway_branch(start_rp, end_rp, TraversalType.NOTPIZZATIME, FG)
        PT = bridge_oneway_branch(end_rp, start_rp, TraversalType.PIZZATIME, FG)

        return BranchSegment(start_rp, end_rp, PT, NPT)
    except RuntimeError as e:
        pass
        
    FG.revert(pre_bridge_FG) 

    raise RuntimeError(f"bridge_branch: failed traversal or room_selection between {start_rp.room} and {end_rp.room}")
    

def bridge_oneway_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, traversal_type: TraversalType, FG: FlowGraphHandler):
    traversal = get_traversal(start_rp, end_rp, FG, traversal_type)
    room_selection = select_rooms(FG, traversal, traversal_type)
    return room_selection

def bridge_self_loop(room: Room, FG: FlowGraphHandler):

    if (not room.needs_self_loop):
        raise ValueError(f"Invalid bridge_self_loop for {room}")

    self_loop = room.self_loop

    if (self_loop == None or type(self_loop) != SelfLoop):
        raise ValueError(f"Invalid bridge_self_loop for {room}, self loop is not defined")

    start_rp = RoomPath(room, self_loop.start)
    end_rp = RoomPath(room, self_loop.end)

    traversal_type = TraversalType.ANY

    match self_loop.path_time:
        case PathTime.NOTPIZZATIME:
            traversal_type = TraversalType.NOTPIZZATIME
        case PathTime.PIZZATIME:
            traversal_type = TraversalType.PIZZATIME
        case PathTime.BOTH:
            if (self_loop.allow_oneway):
                traversal_type = TraversalType.OW
            else:
                traversal_type = TraversalType.ANY
            

    traversal = get_traversal(start_rp, end_rp, FG, traversal_type)
    room_selection = select_rooms(FG, traversal, traversal_type)

    return room_selection

#Iterators that yield every potential combination of start path and end path for the selected SD
#catch errors on bridge failure
#utilize recursion in to maintain position within iterator in case of step-back

def bridge_twoway_room_room(start_room: Room, end_room: Room, FG: FlowGraphHandler):

    match start_room.room_type:
        case RoomType.ENTRANCE:
            return bridge_twoway_from_entrance(start_room, end_room, FG)
        case _:
            raise NotImplementedError(f"{ERROR}ERROR: bridge_twoway_room_room() not implemented for start_room of type {start_room.room_type}{RESET}")

def bridge_branch_room_room(start_room: Room, end_room: Room, FG: FlowGraphHandler):
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
            except RuntimeError as e2:
                pass

def bridge_twoway_from_entrance(start_room: Room, end_room: Room, FG: FlowGraphHandler):

    for start_rp in entrance_room_path(start_room):
        for end_rp in room_path_cap_TW(end_room):
            try:
                yield bridge_twoway(start_rp, end_rp, FG)
            except RuntimeError as e:
                pass

#make bridges from start room with already selected paths
def bridge_twoway_rp_room(start_rp: BaseRoomPath, end_room: Room, FG: FlowGraphHandler):
    i = 0
    s = 0

    for end_rp in room_path_cap_TW(end_room):
        i+=1
        try:
            s += 1
            yield bridge_twoway(start_rp, end_rp, FG)
        except RuntimeError as e:
            pass

def bridge_branch_rp_room(start_rp: BranchRoomPath, end_room: Room, FG: FlowGraphHandler):
    #srp is BS/BA so end_rp is BE/BA
    for end_rp in branch_room_path(end_room, StartExitType.EXIT):
        #branch will connect NPT and PT together, so check both
        try:
            yield bridge_branch(start_rp, end_rp, FG)
        except RuntimeError as e:
            pass


        