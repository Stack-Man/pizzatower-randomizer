from path_traversal import find_path

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
class Level():
    def __init__(self):
        self.segments = [] #List of RoomSegment, PathSegment, and BranchSegment
        self.branch_count = 0

class BranchPath():
    def __init__(self, branch_room):
        self.branch = branch_room.branch_endpoint
        self.NPT = branch_room.NPT_endpoint
        self.PT = branch_room.PT_endpoint
        self.start_exit_type = branch_room.start_exit_type

class BranchSegment():
    def __init__(self, start_branch, OW_NPT, OW_PT, end_branch):
        self.start_branch = start_branch #BranchPath
        self.OW_NPT = OW_NPT #PathSegment
        self.OW_PT = OW_PT #PathSegment
        self.end_branch = end_branch #BranchPath
    
    def get_last_endpoint(self):
        return self.end_path.branch_endpoint

class PathSegment():
    def __init__(self, paths)
        self.paths = paths #List of (endpoint, RoomPath) AKA result of find_path
    
    def get_last_endpoint(self):
        return self.paths[len(self.paths) - 1][0] #endpoint of last entry

class RoomSegment():
    def __init__
        self.path = None #(endpoint, RoomPath)
        self.endpoint = None #endpoint
    
    def get_last_endpoint(self):
        return self.endpoint


#TODO: do all levels construct then go through and grow paths after
def construct_level_from_layers(E, EBS, J, JBE, BS, BE, TW, OW_PT, OW_NPT):
    level = Level()
    
    #choose start
    start_segment = construct_start_segment(E, EBS, JBE, OW_PT, OW_NPT)
    level.segments.append(start_segment)
    
    if isinstance(start_segment, BranchSegment):
        level.branch_count = level.branch_count + 1
    
    max_branches = 1 #TODO: max branch parameter
    prev_segment = start_segment
    
    #choose branches
    while (level.branch_count < max_branches):
        
        A = prev_segment.get_last_endpoint()
        twoway_segment, branch_segment = construct_two_way_to_branch_segment(BS, BE, OW_PT, OW_NPT, TW, A)
        
        level.append(twoway_segment)
        level.append(branch_segment)
        
        level.branch_count = level.branch_count + 1
        
        prev_segment = branch_segment

    #choose end
    A = prev_segment.get_last_endpoint()
    twoway_segment, end_segment = construct_two_way_to_end_segment(J, JBE, BS, OW_PT, OW_NPT, TW, A)
    
    level.append(twoway_segment)
    level.append(end_segment)
    
    if isinstance(end_segment, BranchSegment):
        level.branch_count = level.branch_count + 1

    return level

#TODO: Branch layers currently are lists of BranchRoom
#which contain Door() and Endpoint() objects for the three doors (branch, NPT, PT)
#use this to choose a specific branch and its paths


def construct_two_way_to_branch_segment(BS, BE, OW_PT, OW_NPT, TW, A):
    #choose some BS
    #get F from BS
    
    #find TW from A to F
        #if cant, try new BS
    #find B  from BS to BE
        #if cant, ditch TW and try new BS
    
    #repeat with different BS until some A > TW > B is found
        #if none, report back that the last segment is faulty
    
    #TODO: ditch_path to refund path from find_path
    #TODO: include Endpoint types in RoomPath
    #TODO: some cateogrization of BS/BE so we dont redundantly check branches that will result in the same,
    #maybe remember what type of ends resulted in "failure" where?
    #also need to make a cascading ditch and pick next system if we run out of options on a segment
    
    for F_BS in BS: 
        
        F = F_BS.branch
        
        TW_path_segment = construct_twoway_segment(TW, A, F)
        
        if TW_path is not None:
            
            for F_BE in BE:
            
                B_path_segment = construct_branch_segment(F_BS, F_BE, OW_PT, OW_NPT)
                
                if B_path_segment is None:
                    #TODO: ditch TW
                    break #try next BS
                else:
                    return TW_path_segment, B_path_segment
    
    return None, None #Failed to make TW, BS from A

def construct_two_way_to_end_segment(J, JBE, BS, OW_PT, OW_NPT, TW, A): #TODO: account for max branches
    #choose some J (or JE)
    #get F from J
    
    #TODO: use construct_two_way_to_branch_segment if JE
    #find TW from A to F
        #if cant, try new J or JE
    #if JE find B  from BS to JE
        #if cant, ditch TW and try new JE or J
    
    #repeat with different JE or J until some A > TW > B is found
        #if none, report back that the last segment is faulty
    
    #TODO: ditch_path to refund path from find_path
    #TODO: include Endpoint types in RoomPath
    
    return

#TODO:
#could pass EBS or JBE to construct_branch_segment to get a branchs egment with entrance/exit
#have to construct twoway fillers outside branch segment so we can see A and F
#TODO: have to include ENtrance and John in the same Room picking list thing

def construct_start_segment(E, EBS, JBE, BE, OW_PT, OW_NPT):
    """
    |-Start Segments-|
    Entrance > ...
    Entrance Branch Start > One Way > Branch End > ...      #dont add branch segment if we did this (depending on settings)
    Emtrance Branch Start > One Way > John Branch End       #failsafe if we did EBS but have no valid BE
    """
    
    
    
    return

def construct_branch_segment(A_BS, F_BE, OW_PT, OW_NPT):
    """
    Two OW paths from A_BS to F_BE
    One OW_PT and one OW_NPT
    
    A_BS and F_BE are BranchRooms which contain information
    on the three Endpoints of the Branch
    """
    
    BS_path = BranchPath(A_BS)
    BE_path = BranchPath(F_BE)
    
    #NPT path from BS to BE
    A_NPT = BS_path.NPT
    F_NPT = BE_path.NPT
    
    OW_NPT_path = construct_oneway_segment(OW_NPT, A_NPT, F_NPT)
    
    #PT path from BE to BS
    A_PT = BE_path.PT
    F_PT = BS_path.PT
    
    OW_PT_path = construct_oneway_segment(OW_PT, A_PT, F_PT)
    
    if not OW_NPT_path or not OW_PT_path:
        #TODO: ditch other path if either is None
        return None
    
    branch_segment = BranchSegment(BS_path, OW_NPT_path, OW_PT_path, BE_path)
    
    return branch_segment

def construct_end_segment(J, JBE, BS, TW, OW_PT, OW_NPT):
    """
    |-End Segments-|
    ... > Two Way > John
    ... > Two Way > Branch Start > One Way > John Branch End
    """
    return

def construct_twoway_segment(TW, A, F):
    return construct_segment(TW, A, F, use_oneways = False)

def construct_oneway_segment(OW, A, F):
    #Find path from A to F in OW
    #A and F are from BranchRoom object in Branch Layer
    #The endpoints are already processed to identify Start/Exitness of the endpoint
    
    if A.start_exit_type == StartExitType.START or F.start_exit_type == StartExitType.EXIT:
        raise ValueError("construct oneway has A or F of wrong StartExit type!")
    
    return construct_segment(OW, A, F, use_oneways = True)

def construct_segment(G, A, F, use_oneways):
    #Find path from A to F in G
    
    path = find_path(G, A, F, prioritize_oneway = use_oneways)
    
    if not path:
        return None
    
    path_segment = PathSegment(path)
    
    return path_segment















