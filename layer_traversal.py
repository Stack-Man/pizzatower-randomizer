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
    def __init__(self):
        self.branch_endpoint = None #endpoint
        self.branch_NPT = None #(endpoint, RoomPath) for branch to NPT or NPT to branch
        self.branch_PT = None #(endpoint, RoomPath) for branch to PT or PT to branch

class BranchSegment():
    def __init__(self):
        self.start_branch = None #BranchPath
        self.OW_NPT = None #PathSegment
        self.OW_PT = None #PathSegment
        self.end_branch = None #BranchPath
    
    def get_last_endpoint(self):
        return self.end_path.branch_endpoint

class PathSegment():
    def __init__
        self.paths = [] #List of (endpoint, RoomPath)
    
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

def get_end_endpoint(segment):
    return "TODO get end endpoint"

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
    
    return

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

def construct_start_segment(E, EBS, JBE, OW_PT, OW_NPT, ):
    """
    |-Start Segments-|
    Entrance > ...
    Entrance Branch Start > One Way > Branch End > ...      #dont add branch segment if we did this (depending on settings)
    Emtrance Branch Start > One Way > John Branch End       #failsafe if we did EBS but have no valid BE
    """
    
    return

def construct_branch_segment(BS, BE, OW_PT, OW_NPT):
    """
    |-Branch Segments-|
    Two Way > Branch Start > One Way  > Branch End > ...
    """
    return

def construct_end_segment(J, JBE, BS, TW, OW_PT, OW_NPT):
    """
    |-End Segments-|
    ... > Two Way > John
    ... > Two Way > Branch Start > One Way > John Branch End
    """
    return

def construct_twoway_segment(TW, A, F):
    return

def construct_oneway_segments(OW_PT, OW_NPT, A_PT, F_PT, A_NPT, F_NPT):
    return















