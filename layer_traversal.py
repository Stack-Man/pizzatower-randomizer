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

1. Choose a Start Segment
2. Choose zero or more Branch Segments
3. Choose an End Segment

For any One Way, find two paths connecting both ends of the branch paths.
For any Two Way, find a path of any length connecting the two end layers.

For any other layer, determine the path being used through it.
Branch path should choose a specific path.
"""



def create_level(TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE):
    level = Level()
    
    A_endpoints = E #TODO: option for EBS
    F_endpoints = BS 
    
    #Get A, F and path AF
    #sync AF from TW with OW
    #sync F from BS with BE
    
    print("Create Start Segment")
    
    start_A_endpoint, start_F_endpoint, path_AF = create_bridge_twoway(TW, A_endpoints, F_endpoints, to_sync_G = [OW_NPT, OW_PT], to_sync_F = [BE])
    
    #TODO: if failed, try with F_endpoints = J or with JBE if EBS
    
    start = RoomSegment(start_A_endpoint) 
    start_segment = PathSegment(path_AF)
    
    level.add_segment(start)
    level.add_segment(start_segment)
    
    max_branches = 1 #TODO: parameterize

    #prev_segment = start_segment
    next_is_twoway = False #TODO: switch if we started with EBS
    
    current_A_endpoint = start_A_endpoint
    current_F_endpoint = start_F_endpoint
    
    #TODO TODO: failing branch find, maybe because path before has bad endpoint?
    while (level.branch_count < max_branches): #TODO: maybe make john segment first to increase success rate since john segment is more important
        
        print("Create Branch Segment")
        
        #A = prev_segment.get_last_endpoint()
        A = current_F_endpoint
        A_endpoints = [A]
        
        current_segment = None
        
        if next_is_twoway:
            F_endpoints = BS
            
            #Get A, F and path AF
            #sync AF from TW with OW
            #sync F from BS with BE
            twoway_A_endpoint, twoway_F_endpoint, twoway_path = create_bridge_twoway(TW, A_endpoints, F_endpoints, to_sync_G = [OW_NPT, OW_PT], to_sync_F = [BE])
            
            current_segment = PathSegment(twoway_path)
            current_A_endpoint = twoway_A_endpoint
            current_F_endpoint = twoway_F_endpoint
            
        else: #TODO: option to use JBE
            F_endpoints = BE
            
            #Get A, F and path PT and NPT
            #sync NPT, PT from OW with TW
            #sync F from BE with BS
            branch_A_endpoint, branch_F_endpoint, branch_path_NPT, branch_path_PT = create_bridge_oneway(OW_NPT, OW_PT, A_endpoints, F_endpoints, to_sync_G = [TW], to_sync_BE = [BS])
            
            NPT_segment = PathSegment(branch_path_NPT)
            PT_segment = PathSegment(branch_path_PT)
            
            current_segment = BranchSegment(branch_A_endpoint, NPT_segment, PT_segment, branch_F_endpoint)
            current_A_endpoint = branch_A_endpoint
            current_F_endpoint = branch_F_endpoint
        
        if current_segment == None:
            return level #TODO: back track and try prev segment without the used F, current_F_endpoint
        
        next_is_twoway = not next_is_twoway #flip
        
        level.add_segment(current_segment)
    
    #TODO: skip if used JBE
    A = current_F_endpoint
    A_endpoints = [A]
    F_endpoints = J
    
    #Get A, F and path AF
    #sync AF from TW with OW
    end_A_endpoint, end_F_endpoint, path_AF = create_bridge_twoway(TW, A_endpoints, F_endpoints, to_sync_G = [OW_PT, OW_NPT])
    
    end_segment = PathSegment(path_AF)
    end = RoomSegment(end_F_endpoint)
    
    level.add_segment(end_segment)
    level.add_segment(end)

    return level
















