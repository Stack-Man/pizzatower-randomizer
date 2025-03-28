#Author: Stack Man
#Date: 3-26-2025

from enums import BranchType, RoomType
from objects import Room, PathRequirement, ConnectionRequirement

def check_room_type(Room: room, RoomType: room_type):
    return room.room_type == room_type

def check_room_branch_type(Room: room, BranchType: branch_type):
    return room.branch_type == branch_type

def create_connection_requirement(Room: first_room, Room: last_room, bool: is_return, str: first_path_start_letter = "", str: last_path_exit_letter = ""):

    branch_path_time = PathTime.PIZZATIME if is_return else PathTime.NOTPIZZATIME
    first_exception_type = RoomType.JOHN if is_return else RoomType.ENTRANCE
    last_exception_type = RoomType.ENTRANCE if is_return else RoomType.JOHN

    #If the first room is BranchType.NONE then it is a non-branching entrance
    #Otherwise, it is a start or end using the connection
    first_path_times = [branch_path_time] if ! check_room_branch_type(first_room, BranchType.NONE) else [PathTime.ANY]
    
    #If entrance, no
    #If not, if start, yes
    first_path_start_use_branch = False
    
    if !check_room_type(first_room, first_exception_type) and check_room_branch_type(first_room, BranchType.START)
        first_path_start_use_branch = True
    
    PathRequirement: first_path_requirement = PathRequirement(
        first_path_times, 
        start_letter = first_path_start_letter, 
        start_use_branch = first_path_start_use_branch)
    
    #same as first but if last_room is a non-branching John
    last_path_times =  [branch_path_time] if ! check_room_branch_type(last_room, BranchType.NONE) else [PathTime.ANY]
    
    #If john, no
    #If not, if end, yes
    last_path_exit_use_branch = False
    
    if !check_room_branch_type(last_room, last_exception_type) and check_room_branch_type(last_room, BranchType.END)
        last_path_exit_use_branch = True
    
    PathRequirement: last_path_requirement = PathRequirement(
        last_path_times,
        exit_letter = last_path_exit_letter,
        exit_use_branch = last_path_exit_use_branch)

    ConnectionRequirement: connection_requirement = ConnectionRequirement(
        first_room,
        last_room,
        first_path_requirement,
        None,
        last_path_requirement)    

    return connection_requirement