#Author: Stack Man
#Date: 3-25-2025

from typing import List
from objects import Level, Sequence, Connection, ConnectionRequirements, RoomRequirements, PathRequirements
from enums import PathTime, RoomType, BranchType
from search import *
from tools import *

def create_all_levels(levels: List[Level]):
    
    new_levels = []
    created_war_level = False
    
    for level in levels:
        new_level = create_one_level(level)
        
        if new_level == None and not created_war_level:
            new_level = create_war_level(level)
        
        if new_level != None:
            new_levels.append(new_level)
            
    return new_levels


def create_one_level(level: Level):
    #Create initial sequence
    incomplete_sequence = Sequence(
        None, 
        None, 
        None, 
        level.entrance,
        check_room_branch_type(level.entrance, BranchType.NONE)
        )
    
    #Recursively create rest of sequences
    return create_sequences(incomplete_sequence, "A")


#TODO:
def create_war_level(level: Level):
    pass


sequence_used_room_names: List[str] = []

#TODO: make john rooms have a fake door for the JOHN ?
def create_sequences(current_sequence: Sequence, first_path_start_letter: str):

    #return if to_connection is defined
    if current_sequence.to_connection != None:
        return current_sequence
    
    #should we create a return_connection
    needs_return = not current_sequence.first_room_is_end_branch

    #determine room, path, and branch Requirements
    room_types = [RoomType.ONEWAY, RoomType.TWOWAY] if needs_return else [RoomType.TWOWAY]
    
    branch_type = BranchType.END if needs_return else BranchType.START
    john_branch_type = BranchType.NONE if needs_return else BranchType.END
    all_branch_room_requirements = [RoomRequirements(RoomType.BRANCH, branch_type), 
                         RoomRequirements(RoomType.JOHN, john_branch_type)] #TODO: prioritize john with max branches limit
    
    to_path_times = [PathTime.ANY, PathTime.NOTPIZZATIME] if needs_return else [PathTime.ANY] #to_path must be traversible both ways if no return
    return_path_times = [PathTime.ANY, PathTime.PIZZATIME]
    
    between_room_requirements = RoomRequirements(
        room_types,
        BranchType.NONE,
        PathRequirements(to_path_times)
        )
    
    return_between_room_requirements = RoomRequirements(
        room_types,
        BranchType.NONE,
        PathRequirements(return_path_times)
    )
    
    global sequence_used_rooms

    for branch in get_rooms(all_branch_room_requirements):
        
        to_connection_requirements = create_connection_requirements(Sequence.first_room, branch, False, first_path_start_letter)
        to_connection_requirements.between_room_requirements = between_room_requirements
        
        for to_connection, last_room_start_letter in create_connections(None, to_connection_requirements):
        
            current_sequence.to_connection = to_connection
            sequence_used_rooms = add_connection_rooms_to_list(to_connection, sequence_used_rooms)
            
            #I'm leaving out the last_path loop because I'm assuming that there's only every one valid last path at the end
            #of the connection considering the restrictions with branch doors and path time
            #TODO: maybe make connection creator ignore loop doors in sequence first or last room
            
            if not needs_return:  
                new_sequence = continue_sequence(current_sequence, branch, last_room_start_letter)
                
                if new_sequence != None:
                    return new_sequence
            else:
                
                #branch door and path_times reqs will cause the correct path to be chosen
                #TODO: confirm this is actually the case
                #TODO may not be the case for branching john rooms? may have to reformat john rooms to have two distinct paths one for pizza and one for notpizza
                #or have an exception for them
                return_connection_requirements = create_connection_requirements(branch, Sequence.first_room, True, "", first_path_start_letter)
                return_connection_requirements.branch_room_requirements = return_between_room_requirements

                for return_connection in create_connections(None, return_connection_requirements):
                
                    current_sequence.return_connection = return_connection
                    sequence_used_rooms = add_connection_rooms_to_list(return_connection, sequence_used_rooms)
                    
                    new_sequence = continue_sequence(current_sequence, branch, last_room_start_letter)
                
                    if new_sequence != None:
                        return new_sequence
                    
                    current_sequence.return_connection = None
                    sequence_used_rooms = remove_connection_rooms_from_list(return_connection, sequence_used_rooms)
                    
                    pass
                    
            current_sequence.to_connection = None
            sequence_used_rooms = remove_connection_rooms_from_list(to_connection, sequence_used_rooms)
        
            pass
    
    pass

def continue_sequence(current_sequence: Sequence, last_room: Room, last_room_start_letter: str):

    if not check_room_type(last_room, RoomType.JOHN): 
        incomplete_sequence = Sequence(
            None,
            None,
            None,
            last_room,
            check_room_branch_type(last_room, BranchType.END)
            )
        
        next_sequence = create_sequences(incomplete_sequence, last_room_start_letter)
        
        if next_sequence != None:
            current_sequence.next_sequence = next_sequence
            return current_sequence
        
        return None       
    else:
        return current_sequence


connection_used_exits: List[Door] = []

#yield a complete connection and the start letter of last room
def create_connections(current_connection: Connection, cr: ConnectionRequirements):
    
    #initialization for first round
    if current_connection == None:
        current_connection = Connection(
            requirements.first_room,
            None,
            None
        )
    
    global connection_used_exits

    #trim_paths removes paths from the room that:
    #   * can't connect to the last_path's exit (stored in path requirements)
    #   * have an exit that has already been tried in the current connection string (conection_used_exits)
    #   * or otherwise don't meet the room requirement's path requirements
    for current_path in trim_paths(cr.first_room, cr.first_path_requirements, connection_used_exits):
        current_connection.path = current_path

        #Never try the same exit type in a connection string more than once
        #An exit type that fails to continue to last_room once cannot do so regardles of its room or position in the string
        connection_used_exits.append(current_connection.path.exit_door)
        
        for last_connection, last_path_start_letter in create_connection_last(current_connection, cr):
            yield last_connection, last_path_start_letter


        #the first path of the next connection is a "between" path
        #and its start should connect withthe current_path's exit
        next_connection_requirements = cr.deepcopy()
        next_connection_requirements.first_path_requirements = next_connection_requirements.between_room_requirements.path_requirements
        next_connection_requirements.first_path_requirements.start_door_type = current_path.exit_door.door_type
        next_connection_requirements.first_path_requirements.start_door_dir = opposite_dir(current_path.exit_door.door_dir)


        for next_room in get_rooms(next_connection_requirements.between_room_requirements):
            incomplete_connection = Connection(
                next_room,
                None,
                None
            )

            for next_connection, last_path_start_letter in create_connections(incomplete_connection, next_connection_requirements):
                current_connection.next_connection = next_connection
                yield current_connection, last_path_start_letter
            
            
        current_connection.next_connection = None

    pass

#Tries to create connection to requirements.last_room
#yield: connection with connection to last
def create_connection_last(current_connection: Connection, cr: ConnectionRequirements):
    
    #last_path start must connect to current_path exit
    #TODO: may need an exception to prevent one-ways from being chosen when they shouldn't be (it  was in the original code)
    for path in trim_paths(cr.last_room, cr.last_path_requirements, current_connection.path.exit_door):

        connection_last = Connection(cr.last_room, path, None)
        current_connection.next_connection = connection_last

        yield current_connection, path.start_door.letter

#TODO:
def pad_level(level: Level, rooms_to_reach: int):
    pass

#TODO:
def add_rooms_inbetween(connection: Connection, cr: ConnectionRequirements, max_rooms_to_add: int, is_to_connection: bool = False):
    pass



