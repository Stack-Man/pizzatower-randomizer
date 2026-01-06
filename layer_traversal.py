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
        self.start_segment = None
        self.branch_count = 0
        self.branch_segments = []
        self.end_segment = None

class StartSegment():
    def __init__(self):
        self.entrance = None
        self.is_branch_start = False
        self.OW_NPT = None
        self.OW_PT = None
        self.end = None
        self.is_john_end = False

class BranchSegment():
    def __init__(self):
        self.TW = None
        self.BS = None
        self.OW_NPT = None
        self.OW_PT = None
        self.BE = None


class EndSegment():
    def __init__(self):
        self.TW = None
        self.BS = None
        self.OW_NPT = None
        self.OW_PT = None
        self.end = None
        self.is_branch_end = False


def construct_level_from_layers(E, EBS, J, JBE, BS, BE, TW, OW_PT, OW_NPT):
    
    Level = []
    
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

def construct_branch_segment(BS, BE, TW, OW_PT, OW_NPT):
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















