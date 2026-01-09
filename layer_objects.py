from node_id_objects import StartExitType

#used to create Endpoint from vals directly instead of from NodeID
class FakeNode():
    def __init__(self, type, dir, start_exit_type):
        self.inner_id.door_type = type
        self.inner_id.door_dir = dir
        self.inner_id.start_exit_type = start_exit_type

class BaseRoom():
    def set_endpoint(door, se_type):
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
        self.PT_endpoint = self.set_sendpoint(PT_door, pt_se_type)
    
    def get_twoway_endpoint(self):
        return self.branch_endpoint

class EntranceRoom(BaseRoom):
    def __init__(self, room_name, start_door, exit_door):
        self.room_name = room_name
        self.start_door = start_door
        self.exit_door = exit_door
        
        self.exit_endpoint = self.set_endpoint(exit_door, StartExitType.EXIT)
        self.start_endpoint = self.set_endpoint(start_door, StartExitType.START)
        
    def set_endpoint(door, se_type):
        n = FakeNode(door.door_type, door.door_dir, se_type)
        return Endpoint(n)
    
    def get_twoway_endpoint(self):
        return self.exit_endpoint

class JohnRoom(BaseRoom):
    def __init__(self, room_name, door):
        self.room_name = room_name
        self.door = door
        
        self.door_endpoint = self.set_endpoint(door, StartExitType.START)
    
    def set_endpoint(door, se_type):
        n = FakeNode(door.door_type, door.door_dir, se_type)
        return Endpoint(n)
    
    def get_twoway_endpoint(self):
        return self.door_endpoint