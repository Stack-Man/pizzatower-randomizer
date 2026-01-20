from layer_objects import Level, BranchPathSegment, PathSegment, RoomSegment, EntranceRoom, JohnRoom, EJBranchRoom, BranchRoom

"""
---------------
LEVEL STRUCTURE
---------------

|-Start Segments-|
Entrance > ...
Entrance Branch Start > One Way > Branch End > ...
Emtrance Branch Start > One Way > John Branch End

|-Branch Segments-|
Two Way > Branch Start > One Way  > Branch End > ...

|-End Segments-|
... > Two Way > John
... > Two Way > Branch Start > One Way > John Branch End

-----------------------------
ALGORITHM - CONSTRUCT A LEVEL
-----------------------------

The most recently added segment to Level
is a RoomSegment that contains a list of
A. Viable rooms (start matches prev seg end)
B. Viable john rooms (same but john)

1. Get last RoomSegment
2. Choose viable room V
3. Create segment from V
4. If none Choose viable john J
5. If none, StepBack()

StepBack():
Remove last RoomSegment and Path/BranchSegment
as no viable room was found

Continue from prev last RoomSegment, which
continues to contain its 
"""
from layer_handler import LayerHandler #mangage layer requests and synchronization

def create_level(TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE):

    level = Level()
    layers = LayerHandler(TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE)
    
    max_branches = 1 #TODO: parameterize
    
    #init first RoomSegment with a list of available entrances
    available_entrances = []
    available_entrances.extend(E)
    available_entrances.extend(EBS)
    
    print("Available Entrances: ")
    
    for ae in available_entrances:
        print("     ", ae.room_name, ": ", str(type(ae)))
    
    available_start_rooms = RoomSegment(available_entrances, [], False)
    
    level.add_segment(available_start_rooms)
    
    while (True):
        
        last_room_seg = level.get_last_room_seg()
        successful = False
        john_end = False
        want_john_end = level.branch_count >= max_branches
       
        #Create start segment
        if level.segment_count() == 1:
            print("Add Entrance")
            
            #cant do john end bc no john in last room seg, 
            #immediate john end would come from other add segments
            successful = add_entrance_segments(level, layers, last_room_seg)
            
            #If Failed, level is fail!
            if not successful:
                print("Failed Level")
                return None

        elif last_room_seg.is_branch_end:
            print("Add Twoway")
            
            #Bridge Twoway from last branch to new branch or J if none
            successful, john_end = add_twoway_segments(level, layers, last_room_seg, want_john_end)
        else:
            print("Add Branch")
            
            #Create branch segment to BE or JBE if none
            successful, john_end = add_branch_segments(level, layers, last_room_seg, want_john_end)
        
        if not successful: #if none, step back
            print("Step Back. Not successful.")
            step_back(level, layers)
            continue
        elif john_end:
            return level
        elif level.branch_count > max_branches: #TODO: doesnt really force a john endad any point
            print("Step Back too many branches")
            step_back(level, layers)
            continue
        else:
            continue

    return level

def step_back(level, layers):
    #No viable room from last room segment
    #and path to those last rooms must be bad too
    room_seg = level.remove_last_segment()
    path_seg = level.remove_last_segment()
    
    layers.refund_seg(room_seg) #ultimately refunds nothing bc there is no chosen room
    layers.refund_seg(path_seg)
    
    #normally a chosen room is refunded when it first fails
    #but in the case of a step back, we need to refund it ourselves
    prev_room_seg = level.get_last_room_seg()
    layers.refund_room(prev_room_seg.chosen_room)
    
    
#TODO: could have john be forbidden if below certain branch, then do another run with john if cant find any
#TODO: let john/entrance room choose any door instead of specific one
def add_path_to_level(level, path, valid_rooms, valid_johns):
    #chosen room of prev Room is set when getting it in add segment
    
    #add path seg
    path_seg = PathSegment(path)
    level.add_segment(path_seg)
    
    #add room seg with viable rooms
    #end of twoway = J/BS
    room_seg = RoomSegment(valid_rooms, valid_johns, is_branch_end = False)
    level.add_segment(room_seg)

def add_branch_to_level(level, path_NPT, path_PT, valid_rooms, valid_johns):
    #chosen room of prev Room is set when getting it in add segment
    
    #add branch seg
    branch_seg = BranchPathSegment(path_NPT, path_PT)
    level.add_segment(branch_seg)
    
    #add room seg with viable rooms
    #end of branch = JBE/BE
    room_seg = RoomSegment(valid_rooms, valid_johns, is_branch_end = True)
    level.add_segment(room_seg)

def add_entrance_segments(level, layers, last_room_seg):
    #create twoway bridge: E > TW > BS/J
    #OR
    #create oneway bridge: EBS > OW > BE/JBE
    
    while True:
        
        chosen_room = layers.get_viable_entrance(last_room_seg) #also sets
    
        if chosen_room is None:
            return False #Failed! (no viable john bc start)
    
        #differentiate E from EBS in last_room_seg using class type: EntranceRoom vs BranchRoom
        if isinstance(chosen_room, EntranceRoom):
            chosen_A, chosen_F, path_AF = layers.bridge_twoway(chosen_room)
            
            if chosen_F is None:
                layers.refund_entrance(chosen_room)
                continue
            
            valid_rooms, valid_johns = layers.get_matching_J_BS(chosen_F)
            add_path_to_level(level, path_AF, valid_rooms, valid_johns)
            
            return True
        
        else:
            chosen_BS, chosen_BE, path_NPT, path_PT = layers.bridge_oneway(chosen_room)
            
            if chosen_BE is None:
                layers.refund_entrance(chosen_room)
                continue
            
            valid_rooms, valid_johns = layers.get_matching_JBE_BE(chosen_BE)
            add_branch_to_level(level, path_NPT, path_PT, valid_rooms, valid_johns)
            
            return True

def add_branch_segments(level, layers, last_room_seg, want_john_end):
    #create oneway bridge: last_room_seg (viable BSs) > OW > BE/JBE
    #or
    #choose J from REMOVE SEG
    
    while True:
        if want_john_end: #force john so we dont add another branch
            print("Force John")
            break
        
        chosen_room = layers.get_viable_branch_start(last_room_seg) #also sets
        
        if chosen_room is None:
            print("Branch fail try john")
            break #try john
        
        print("Try branch with", chosen_room.room_name)
        
        chosen_BS, chosen_BE, path_NPT, path_PT = layers.bridge_oneway(chosen_room)
        
        if chosen_BE is None:
            layers.refund_branch_start(chosen_room)
            continue
        
        valid_rooms, valid_johns = layers.get_matching_JBE_BE(chosen_BE)
        add_branch_to_level(level, path_NPT, path_PT, valid_rooms, valid_johns)
        
        return True, False #success but not john
    
    while True:
        chosen_room = layers.get_viable_john(last_room_seg) #also sets
            
        if chosen_room is None:
            print("No john")
            return False, False #Failed!
            
        #dont add to level because last_room_seg.get already set chosen room
        
        return True, True #success and john


def add_twoway_segments(level, layers, last_room_seg, want_john_end):
    #create oneway bridge: last_room_seg (viable BSs) > OW > BE/JBE
    #or
    #choose J from last_room_seg
    
    while True:
        #if want_john_end: #dont force john so we can try for a twoway john if possible
            #print("Force John")
            #break
        
        #get room and sync
        chosen_room = layers.get_viable_branch_end(last_room_seg) #also sets
            
        if chosen_room is None:
            break #try john
        
        chosen_A, chosen_F, path_AF = layers.bridge_twoway(chosen_room)
        
        if chosen_F is None:
            layers.refund_branch_end(chosen_room)
            continue
        
        valid_rooms, valid_johns = layers.get_matching_J_BS(chosen_F)
        add_path_to_level(level, path_AF, valid_rooms, valid_johns)
        
        return True, False #success but not john
    
    while True:
        chosen_room = layers.get_viable_john(last_room_seg) #also sets
        
        if chosen_room is None:
            print("No John")
            return False, False #Failed!
            
        #dont add to level because last room seg.get already set
        
        return True, True #success and john
















