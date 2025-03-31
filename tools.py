#Author: Stack Man
#Date: 3-26-2025

from typing import List
from enums import BranchType, RoomType, PathTime, DoorDir
from objects import Room, PathRequirements, ConnectionRequirements, Path, Door, Connection, Sequence

def check_room_type(room: Room, room_type : RoomType):
    return room.room_type == room_type

def check_room_branch_type(room: Room, branch_type: BranchType):
    return room.branch_type == branch_type

def exit_matches(path: Path, exits: List[Door]):
    exit_door = path.exit_door

    for exit in exits:
        if exit_door.door_type == exit.door_type and exit_door.door_dir == exit.door_dir: 
            return True

    return False

def doors_connect(a: Door, b: Door):
    return a.door_type == b.door_type and a.door_dir == opposite_dir(b.door_type)

def create_connection_requirements(first_room: Room, last_room: Room, is_return: bool, first_path_start_letter: str = "", last_path_exit_letter: str = ""):
    """Doesn't create the between_room_requirements, that is created separately outside this function"""

    branch_path_time = PathTime.PIZZATIME if is_return else PathTime.NOTPIZZATIME
    first_exception_type = RoomType.JOHN if is_return else RoomType.ENTRANCE
    last_exception_type = RoomType.ENTRANCE if is_return else RoomType.JOHN

    #If the first room is BranchType.NONE then it is a non-branching entrance
    #Otherwise, it is a start or end using the connection
    first_path_times = [branch_path_time] if not check_room_branch_type(first_room, BranchType.NONE) else [PathTime.ANY]
    
    #If entrance, no
    #If not, if start, yes
    first_path_start_use_branch = False
    
    if not check_room_type(first_room, first_exception_type) and check_room_branch_type(first_room, BranchType.START):
        first_path_start_use_branch = True
    
    first_path_requirements = PathRequirements(
        first_path_times, 
        start_letter = first_path_start_letter, 
        start_use_branch = first_path_start_use_branch)
    
    #same as first but if last_room is a non-branching John
    last_path_times =  [branch_path_time] if not check_room_branch_type(last_room, BranchType.NONE) else [PathTime.ANY]
    
    #If john, no
    #If not, if end, yes
    last_path_exit_use_branch = False
    
    if not check_room_branch_type(last_room, last_exception_type) and check_room_branch_type(last_room, BranchType.END):
        last_path_exit_use_branch = True
    
    last_path_requirements = PathRequirements(
        last_path_times,
        exit_letter = last_path_exit_letter,
        exit_use_branch = last_path_exit_use_branch)

    connection_requirements = ConnectionRequirements(
        first_room,
        last_room,
        first_path_requirements,
        None,
        last_path_requirements)    

    return connection_requirements


def yield_sequences(sequence: Sequence):
    current_sequence = sequence

    while (current_sequence != None):
        next_sequence = current_sequence.next_seqeunce
        yield current_sequence
        current_sequence = next_sequence

def yield_connections(connection: Connection):
    current_connection = connection

    #save next_connection first in yielded connection's next is modified
    #we want to iterate over only the original connections when padding
    while (current_connection != None):
        next_connection = current_connection.next_connection
        yield current_connection
        current_connection = next_connection

def add_connection_rooms_to_list(connection: Connection, rooms: List[str]) -> List[str]:

    for c in yield_connections(connection):
        rooms.append(c.room.name)

    return rooms

def remove_connection_rooms_from_list(connection: Connection, rooms: List[str]) -> List[str]:

    for c in yield_connections(connection):
        rooms.remove(c.room.name)

    return rooms

def count_rooms(sequence: Sequence):
    total = 0

    for seq in yield_sequences(sequence):
        total += count_rooms_in_connection(seq.to_connection)
        total += count_rooms_in_connection(seq.return_connection)

    return total

def count_rooms_in_connection(connection: Connection):
    total = 0

    for con in yield_connections(connection):
        total += 1

    return total

#TODO:
def opposite_dir(type: DoorDir):
    pass















