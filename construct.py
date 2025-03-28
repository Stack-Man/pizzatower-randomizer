#Author: Stack Man
#Date: 3-25-2025

from objects import Level, Sequence, RoomRequirements
import search
import tools

def create_all_levels([Level]: levels):
    
	new_levels = []
	created_war_level = False
	
	for level in levels:
		new_level = create_one_level(level)
		
		if new_level == None and !created_war_level:
			new_level = create_war_level(level)
		
		if new_level != None:
			new_levels.append(new_level)
	
    return new_levels


def create_one_level(Level: level):

	#Create initial sequence
	Sequence: incomplete_sequence = Sequence(
		None, 
		None, 
		None, 
		level.entrance,
		check_room_branch_type(level.entrance, BranchType.NONE)
        )
	
	#Recursively create rest of sequences
	return create_sequences(incomplete_sequence, "A")


#TODO: use yield generators to get connections instead of finding all of them
#TODO: make john rooms have a fake door for the JOHN
#TODO: define ONEWAY_TYPES and TWOWAY_TYPES
def create_sequences(Sequence: current_sequence, str: first_path_start_letter):

    #return if to_connection is defined
    if current_sequence.to_connection != None:
        return current_sequence
    
    #should we create a return_connection
    needs_return = !current_sequence.first_room_is_end_branch
    
    #determine room, path, and branch requirements
    room_types = ONEWAY_TYPES if needs_return else TWOWAY_TYPES
    
    branch_type = BranchType.END if needs_return else BranchType.START
    john_branch_type = BranchType.NONE if needs_return else BranchType.END
    room_requirements = [RoomRequirements(RoomType.BRANCH, branch_type), 
                         RoomRequirements(RoomType.JOHN, john_branch_type)] #TODO: prioritize john with max branches limit
    
    to_path_times = [PathTime.ANY, PathTime.NOTPIZZATIME] if needs_return else [PathTime.ANY] #to_path must be traversible both ways if no return
    return_path_times = [PathTime.ANY, PathTime.PIZZATIME]
    
    for branch in get_rooms(room_requirements):
        
        to_connection_requirement = create_connection_requirement(Sequence.first_room, branch, False, first_path_start_letter)
        PathRequirement: between_path_requirement = PathRequirement(to_path_times)
        to_connection_requirement.between_path_requirements = between_path_requirement
        
        #TODO: return last path letter as well from create connections?
        for to_connection, last_room_start_letter in create_connections(to_connection_requirement):
        
            #TODO: add connection rooms to temp_sequence_rooms so they aren't used deeper in the sequence
            current_sequence.to_connection = to_connection
            
            #I'm leaving out the last_path loop because I'm assuming that there's only every one valid last path at the end
            #of the connection considering the restrictions with branch doors and path time
            #TODO: make connection creator ignore loop doors in sequence first or last room?
            
            if !needs_return:  
                new_sequence = continue_sequence(current_sequence, branch, last_room_start_letter)
                
                if new_sequence != None:
                    return new_sequence
            else:
                
                #branch door and path_times reqs will cause the correct path to be chosen
                #TODO: confirm this is actually the case
                #TODO may not be the case for branching john rooms? may have to reformat john rooms to have two distinct paths one for pizza and one for notpizza
                return_connection_requirement = create_connection_requirement(branch, Sequence.first_room, True, "", first_path_start_letter)
                
                for return_connection in create_connection(return_connection_requirement):
                
                    #TODO: add return connection rooms to temp
                    current_sequence.return_connection = return_connection
                    
                    new_sequence = continue_sequence(current_sequence, branch, last_room_start_letter)
                
                    if new_sequence != None:
                        return new_sequence
                    
                    #TODO: remove return connection rooms from temp
                    current_sequence.return_connection = None
                    
                    pass
                    
            #TODO: remove connection rooms from temp since they weren't used
            current_sequence.to_connection = None
        
            pass
    
	pass

def continue_sequence(Sequence: current_sequence, Room: last_room, str: last_room_start_letter):

    if !check_room_type(last_room, RoomType.JOHN): 
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







