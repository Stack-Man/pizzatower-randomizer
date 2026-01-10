from node_id_objects import StartExitType
from path_objects import Endpoint

#==============
#LAYER CREATION
#==============
#used to create Endpoint from vals directly instead of from NodeID
class FakeInnerNode():
    def __init__(self):
        self.door_type = None
        self.door_dir = None
        self.start_exit_type = None

class FakeNode():
    def __init__(self, type, dir, start_exit_type):
        self.inner_id = FakeInnerNode()
        self.inner_id.door_type = type
        self.inner_id.door_dir = dir
        self.inner_id.start_exit_type = start_exit_type

class BaseRoom():
    def set_endpoint(self, door, se_type):
        n = FakeNode(door.door_type, door.door_dir, se_type)
        return Endpoint(n)
    
    def get_twoway_endpoint(self):
        return None
    

#branch layers are lists of BranchRoom
class BranchRoom(BaseRoom):
    def __init__(self, room_name, start_exit_type, branch_door, NPT_door, PT_door):
        self.room_name = room_name
        self.branch_door = branch_door
        self.NPT_door = NPT_door
        self.PT_door = PT_door
        
        self.start_exit_type = start_exit_type
        branch_se_type = start_exit_type
        pt_se_type = branch_se_type
        npt_se_type = StartExitType.START if start_exit_type == StartExitType.EXIT else StartExitType.EXIT #opposite of branch
        
        #if branch is enter, we exit via NPT and enter PT
        #if branch is exit, we enter via NPT and exit PT
        
        self.branch_endpoint = self.set_endpoint(branch_door, branch_se_type)
        self.NPT_endpoint = self.set_endpoint(NPT_door, npt_se_type)
        self.PT_endpoint  = self.set_endpoint(PT_door, pt_se_type)
    
    def get_twoway_endpoint(self):
        return self.branch_endpoint
    
    def __str__(self):
        return self.room_name + ": B: " + str(self.branch_door) + ", NPT: " + str(self.NPT_door) + ", PT: " + str(self.PT_door)

class EntranceJohnRoom(BaseRoom):
    def __init__(self, room_name, door, se_type): #start for John and exit for entrance
        self.room_name = room_name
        self.door = door
        
        self.door_endpoint = self.set_endpoint(door, se_type)
    
    def set_endpoint(self, door, se_type):
        n = FakeNode(door.door_type, door.door_dir, se_type)
        return Endpoint(n)
    
    def get_twoway_endpoint(self):
        return self.door_endpoint
    
    def __str__(self):
        return self.room_name + ": " + str(self.door)

#===============
#LAYER TRAVERSAL
#===============
class Level():
    def __init__(self):
        self.segments = [] #List of class inherited from BaseSegment
        self.branch_count = 0

    def add_segment(self, seg):
        
        self.segments.append(seg)
        
        if isinstance(seg, BranchSegment):
            self.branch_count = self.branch_count + 1
        
class BranchPath(): #Unused?
    def __init__(self, branch_room):
        self.branch = branch_room.branch_endpoint
        self.NPT = branch_room.NPT_endpoint
        self.PT = branch_room.PT_endpoint
        self.start_exit_type = branch_room.start_exit_type

class BaseSegment():
     def get_last_endpoint(self):
        return None

class BranchSegment(BaseSegment):
    def __init__(self, start_branch, OW_NPT, OW_PT, end_branch):
        self.start_branch = start_branch #BranchRoom
        self.OW_NPT = OW_NPT #PathSegment
        self.OW_PT = OW_PT #PathSegment
        self.end_branch = end_branch #BranchRoom
    
    def get_last_endpoint(self):
        return self.end_path.branch_endpoint
    
    def __str__(self):
        if self.start_branch == None or self.end_branch == None:
            return "None branch"
        
        return "NPT: " + self.start_branch.room_name + " > " + str(OW_NPT) + " > " + self.end_branch.room_name + "\n" + "PT: " + self.start_branch.room_name + " < " + str(OW_PT) + " < " + self.end_branch.room_name

class PathSegment(BaseSegment):
    def __init__(self, paths):
        self.paths = paths #List of (endpoint, RoomPath) AKA result of find_path
    
    def get_last_endpoint(self):
        return self.paths[len(self.paths) - 1][0] #endpoint of last entry
    
    def __str__(self):
        
        if self.paths == None:
            return "None Path"
        
        msg = ""
        
        for p in self.paths:
            
            msg += ">" + str(p[1]) + ">"
        
        return msg

class RoomSegment(BaseSegment):
    def __init__(self, room):
        self.room = room #BaseRoom
    
    def get_last_endpoint(self):
        return self.room.get_twoway_endpoint
    
    def __str__(self):
        if (self.room is None):
            return "None Room"
        
        return self.room.room_name