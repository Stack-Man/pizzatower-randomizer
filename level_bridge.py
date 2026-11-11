#Author: Stack Man
#Date: 11/9/2026

#Bridge two rooms using the Flow Graph and select their rooms

from objects import Room, Door, Path
from colors import WARNING, RESET, ERROR
from level_objects import TwowaySegment, BranchSegment, RoomSelection, RoomPath, BranchRoomPath, BaseRoomPath

from enums import PathTime, RoomType, DoorType

from graph_collapse import pairs

def bridge_twoway(start_rp: BaseRoomPath, end_rp: BaseRoomPath, FG):
    print(f"{WARNING} bridge_twoway() not implemented in level_bridge.py")

    #1. take end type of start rp and start type of end rp
    #2. take any TR traversal from FG that matches and whose edges are > 0
    #3. select the rooms to fill the edges (avoiding an impossible booking using the bipartite graphs, if applicable)
    #4. decrease count of edges based on rooms selected

    return TwowaySegment(start_rp, end_rp, RoomSelection([]))

def bridge_branch(start_rp: BranchRoomPath, end_rp: BranchRoomPath, FG):
    print(f"{WARNING} bridge_branch() not fully implemented in level_bridge.py")

    NPT = bridge_oneway_branch(start_rp, end_rp, PathTime.NOTPIZZATIME, FG)
    PT = bridge_oneway_branch(end_rp, start_rp, PathTime.PIZZATIME, FG)

    return BranchSegment(start_rp, end_rp, PT, NPT)

def bridge_oneway_branch(start_room: BranchRoomPath, end_room: BranchRoomPath, path_time: PathTime, FG):
    print(f"{WARNING}bridge_oneway_from_branch() in level_generate.py not implemented{RESET}")
    return RoomSelection([])

def bridge_twoway_room_room(start_room: Room, end_room: Room, FG):
    match start_room.room_type:
        case RoomType.ENTRANCE:
            return bridge_twoway_from_entrance(start_room, end_room, FG)
        case _:
            raise ValueError(f"{ERROR}ERROR: bridge_twoway_room_room() not implemented for start_room of type {start_room.room_type}{RESET}")

def bridge_branch_room_room(start_room: Room, end_room: Room, FG):
    print(f"{WARNING}bridge_branch() in level_generate.py not implemented{RESET}")

    #TODO: try and catch instead of return first
    for start_rp in branch_room_path(start_room):
        for end_rp in branch_room_path(end_room):
            return bridge_branch(start_rp, end_rp, FG)

def bridge_twoway_from_entrance(start_room: Room, end_room: Room, FG):
    #TODO: catch fails

    for start_rp in entrance_room_path(start_room):
        for end_rp in room_path(end_room):
            return bridge_twoway(start_rp, end_rp, FG)

#make bridges from start room with already selected paths
def bridge_twoway_rp_room(start_rp: BaseRoomPath, end_room: Room, FG):
    for end_rp in room_path(end_room):
        return bridge_twoway(start_rp, end_rp, FG)

def bridge_branch_rp_room(start_rp: BranchRoomPath, end_room: Room, FG):
    print(f"{WARNING}bridge_branch_from_room_path() in level_generate.py not implemented{RESET}")

    #TODO: catch fails

    for end_rp in branch_room_path(end_room):
        return bridge_branch(start_rp, end_rp, FG)


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
        