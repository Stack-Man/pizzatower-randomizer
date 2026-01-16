from path_traversal import create_bridge_twoway, create_bridge_oneway
from layer_objects import Level, BranchPath, BranchSegment, PathSegment, RoomSegment


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

def create_level(TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE)

    level = Level()
    
    max_branches = 1 #TODO: parameterize
    
    available_entrances = []
    available_entrances.extend(E)
    available_entrances.extend(EBS)
    
    available_start_rooms = RoomSegment(available_entrances, [], False)
    
    level.add_segment(available_start_rooms)
    
    while (True):
        
        last_room_seg = level.get_last_room_seg()
        successful = False
        john_end = False
       
        #Create start segment
        if level.segment_count() == 1:
            #cant do john end bc no john in last room seg, 
            #immediate john end would come from other add segments
            successful = add_entrance_segments(level, TW, OW_NPT, OW_PT, BS, BE, last_room_seg)
            
            #If Failed, level is fail!
            if not successful:
                return None

        elif last_room_seg.is_branch_end:
            #Bridge Twoway from last branch to new branch or J if none
            successful, john_end = add_twoway_segments(level, TW, OW_NPT, OW_PT, BS, BE, last_room_seg)
        else:
            #Create branch segment to BE or JBE if none
            successful, john_end = add_branch_segments(level, TW, OW_NPT, OW_PT, BE, BE, last_room_seg)
        
        if not successful: #if none, step back
            step_back(level)
            continue
        elif john_end:
            return level
        elif level.branch_count >= max_branches:
            step_back(level)
            continue
        else:
            continue

    return level

def step_back(level):
    #No viable room from last room segment
    #and path to those last rooms must be bad too
    room_seg = level.remove_last_segment()
    path_seg = level.remove_last_segment()
    
    #TODO TODO: refund removed segments

#TODO: could have john be forbidden if below certain branch, then do another run with john if cant find any
#TODO: let john/entrance room choose any door instead of specific one

#TODO: turn repeated code into smaller funcs

def add_entrance_segments(level, TW, OW_NPT, OW_PT, BS, BE, last_room_seg):
    #create twoway bridge: E > TW > BS/J
    #OR
    #create oneway bridge: EBS > OW > BE/JBE
    
    while True:
        
        start = last_room_seg.get_viable_room()
    
        if start is None:
            return False #Failed! (no viable john bc start)
    
        #differentiate E from EBS in last_room_seg using class type: EntranceJohnRoom vs BranchRomo
        if isinstance(start, EntranceRoom):
            #dont sync F bc it has not been finalized
            #dont sync A, nothing to sync to (E)
            chosen_A, chosen_F, path_AF = create_twoway_bridge(G = TW, As = [start], Fs = BS, to_sync_G = [OW_NPT, OW_PT], to_sync_A = [], to_sync_F = []) 
            
            if chosen_F is None:
                continue
            
            #TODO: find alternative Js and BSs that can fit
            
            #TODO: convert to segments and add to level
            #TODO: mark is_branch_end if so
            
            return True
            
        else:
            #dont sync BE to BS bc it has not been finalized
            #dont sync BS to BE bc BS is an EBS
            chosen_BS, chosen_BE, path_NPT, path_PT = create_bridge_oneway(G_NPT = OW_NPT, G_PT = OW_PT, BSs = [start], BEs = BE, to_sync_G = [TW], to_sync_BS = [], to_sync_BE = [])
            
            if chosen_BE is None:
                continue
            
            #TODO: find alternative JBEs and BEs that can fit
            
            #TODO: convert to segments and add to level
            
            return True

def add_branch_segments(level, TW, OW_NPT, OW_PT, BS, BE, last_room_seg):
    
    #create oneway bridge: last_room_seg (viable BSs) > OW > BE/JBE
    #or
    #choose J from last_room_seg
    
    while True:
        
        start = last_room_seg.get_viable_room():
            
        if start is None:
            break #try john
        
        #dont sync BE bc it has not been finalized
        #DO sync BS to BS, BE bc we just chose it
        chosen_BS, chosen_BE, path_NPT, path_PT = create_bridge_oneway(G_NPT = OW_NPT, G_PT = OW_PT, BSs = [start], BEs = BE, to_sync_G = [TW], to_sync_BS = [BS, BE], to_sync_BE = []) 
        
        if chosen_BE is None:
                continue
            
        #TODO: find alternative JBEs and BEs that can fit
        #TODO: mark is_branch_end if so
        
        #TODO: convert to segments and add to level
        
        return True, False #success but not john
    
    while True:
        start = last_room_seg.get_viable_john_room():
            
        if start is None:
            return False, False #Failed!
            
        #TODO: convert to segments and add to level
        
        return True, True #success and john


def add_twoway_segments(level, TW, OW_NPT, OW_PT, BS, BE, last_room_seg):
    #create oneway bridge: last_room_seg (viable BSs) > OW > BE/JBE
    #or
    #choose J from last_room_seg
    
    while True:
        
        start = last_room_seg.get_viable_room():
            
        if start is None:
            break #try john
        
        #dont sync F bc it has not been finalized
        #DO sync A to BS, BE bc we just chose it
        chosen_A, chosen_F, path_AF = create_bridge_twoway(G = TW, As = [start], Fs = BS, to_sync_G = [OW_NPT, OW_PT], to_sync_A = [BS, BE], to_sync_F = [])
        
        if chosen_F is None:
                continue
            
        #TODO: find alternative JBEs and BEs that can fit
        #TODO: mark is_branch_end if so
            
        #TODO: convert to segments and add to level
        
        return True, False #success but not john
    
    while True:
        start = last_room_seg.get_viable_john_room():
            
        if start is None:
            return False, False #Failed!
            
        #TODO: convert to segments and add to level
        
        return True, True #success and john
















