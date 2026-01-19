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

class EJBranchRoom(BaseRoom):
    def __init__(self, room_name, start_exit_type, NPT_door, PT_door):
        self.room_name = room_name
        self.NPT_door = NPT_door
        self.PT_door = PT_door
        
        self.start_exit_type = start_exit_type

        pt_se_type = start_exit_type
        npt_se_type = StartExitType.START if start_exit_type == StartExitType.EXIT else StartExitType.EXIT #opposite of branch
        
        #if branch is enter, we exit via NPT and enter PT
        #if branch is exit, we enter via NPT and exit PT

        self.NPT_endpoint = self.set_endpoint(NPT_door, npt_se_type)
        self.PT_endpoint  = self.set_endpoint(PT_door, pt_se_type)
    
    def get_twoway_endpoint(self):
        raise RuntimeError("EJ Branch does not have a twoway endpoint!")
    
    def __str__(self):
        return self.room_name + ", NPT: " + str(self.NPT_door) + ", PT: " + str(self.PT_door)

class EntranceRoom(BaseRoom):
    def __init__(self, room_name, door):
        self.room_name = room_name
        self.door = door
        
        self.door_endpoint = self.set_endpoint(door, StartExitType.EXIT) #exit bc we leaving the entrance oom
    
    def set_endpoint(self, door, se_type):
        n = FakeNode(door.door_type, door.door_dir, se_type)
        return Endpoint(n)
    
    def get_twoway_endpoint(self):
        return self.door_endpoint
    
    def __str__(self):
        return self.room_name + ": " + str(self.door)

class JohnRoom(BaseRoom):
    def __init__(self, room_name, door):
        self.room_name = room_name
        self.door = door
        
        self.door_endpoint = self.set_endpoint(door, StartExitType.START) #start bc we entering the john room
    
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
        
        if isinstance(seg, BranchPathSegment):
            self.branch_count = self.branch_count + 1
    
    def remove_last_segment(self):
        
        if self.segment_count() > 0:
            seg = self.segments.pop()
            
            if isinstance(seg, BranchPathSegment):
                self.branch_count = self.branch_count - 1
        
            return seg
        
        return None
    
    def segment_count(self):
        return len(self.segments)
    
    def get_last_room_seg(self):
        
        last_room_seg = self.segments[len(self.segments) - 1]
        
        if not isinstance(last_room_seg, RoomSegment):
            raise RuntimeError("last segment added was not a room segment!")
        else:
            return last_room_seg

class BaseSegment():
     def get_last_endpoint(self):
        return None

class BranchPathSegment(BaseSegment):
    def __init__(self, OW_NPT, OW_PT):
        self.OW_NPT = OW_NPT #PathSegment
        self.OW_PT = OW_PT #PathSegment
    
    def __str__(self):
        if self.start_branch == None or self.end_branch == None:
            return "None branch"
        
        return "Branch: \n      NPT: " + self.start_branch.room_name + " > " + str(self.OW_NPT) + " > " + self.end_branch.room_name + "\n" + "      PT: " + self.end_branch.room_name + " > " + str(self.OW_PT) + " > " + self.start_branch.room_name

class PathSegment(BaseSegment):
    def __init__(self, paths):
        self.paths = paths #List of (endpoint, RoomPath) AKA result of find_path
    
    def __str__(self):
        
        if self.paths == None:
            return "None Path"
        
        msg = "Path:    "
        
        for p in self.paths:
            
            msg += ">" + str(p[0]) + ", " + str(p[1])
        
        return msg

class RoomSegment(BaseSegment):
    def __init__(self, others, johns, is_branch_end):
        self.chosen_room = None #BaseRoom
        self.other_viable_rooms = others
        self.john_viable_rooms = johns
        self.is_branch_end = is_branch_end
    
    def __str__(self):
        if (self.room is None):
            return "None Room"
        
        return "Room: " + self.room.room_name
    
    def get_viable_room(self):
        if len(self.other_viable_rooms) == 0:
            return None
        else:
            r = self.other_viable_rooms.pop()
            self.chosen_room = r
            return r

    def get_viable_john(self):
        if len(self.other_viable_rooms) == 0:
            return None
        else:
            r = self.other_viable_rooms.pop()
            self.chosen_room = r
            return r