#Authoren: Stack Man
#Date: 3-25-2025

from objects import Level, Sequence

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
		level.entrance.branch_type == BranchType.NONE)
	
	#Recursively create rest of sequences
	return create_sequences_begin(incomplete_sequence, "A")


#TODO: use yield generators to get connections instead of finding all of them
def create_sequences(Sequence: current_sequence, str: start_letter):
	pass


def continue_sequence(Sequence: current_sequence, str: start_letter):
	pass









