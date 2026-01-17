from path_traversal import create_bridge_twoway, create_bridge_oneway
from layer_objects import Level, BranchPath, BranchSegment, PathSegment, RoomSegment
from path_graph import update_other_G


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
def sync_base_room_lists(to_remove, others):
    #TODO TODO: wont work bc the objects in BS and BE are dif
    #need to use room name?
    #and need some way to refund correctly when we abandon a synced room
    #TODO: use this or sync in get_viable_X?
    
    for O in others:
        if to_remove in O:
            O.remove(to_remove)

#store and manage synchronization of layers
#all requests for paths from layers should be
#done through this class
class Layers():
    
    def __init__(self, TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE):
        self.TW = TW
        self.OW_NPT = OW_NPT
        self.OW_PT = OW_PT
        self.BS = BS
        self.BE = BE
        self.E = E
        self.EBS = EBS
        self.J = J
        self.JBE = JBE

    #TODO TODO: path is None catch
    
    def entrance_bridge_twoway(self, A):
        #Allow BS or J to be chosen for F
        Fs = self.BS
        Fs.extend(self.J)
        
        #dont sync F bc it has not been finalized
        #dont sync A, nothing to sync to (E)
        chosen_A, chosen_F, path_AF = create_bridge_twoway(G = self.TW, As = [A], Fs = Fs)
        
        path_graph.update_other_G((self.TW, [self.OW_NPT, self.OW_PT])
        
        return chosen_A, chosen_F, path_AF
    
    def entrance_bridge_oneway(self, A):
        #Allow BE or JBE to be chosen for BE
        BEs = self.BE
        BEs.extend(self.JBE)
        
        #dont sync BE to BS bc it has not been finalized
        #dont sync BS to BE bc BS is an EBS
        chosen_BS, chosen_BE, path_NPT, path_PT = create_bridge_oneway(G_NPT = self.OW_NPT, G_PT = self.OW_PT, BSs = [A], BEs = BEs)
        
        path_graph.update_other_G(self.OW_NPT, [TW])
        path_graph.update_other_G(self.OW_PT, [TW])
        
        return chosen_BS, chosen_BE, path_NPT, path_PT
    
    def branch_bridge_oneway(self, A):
        #Allow BE or JBE to be chosen for BE
        BEs = self.BE
        BEs.extend(self.JBE)
        
        chosen_BS, chosen_BE, path_NPT, path_PT = create_bridge_oneway(G_NPT = self.OW_NPT, G_PT = self.OW_PT, BSs = [A], BEs = BEs) 
        
        path_graph.update_other_G(self.OW_NPT, [TW])
        path_graph.update_other_G(self.OW_PT, [TW])
        
        #dont sync BE bc it has not been finalized
        #DO sync BS to BS, BE bc we just chose it
        sync_base_room_lists(chosen_BS, [self.BS, self.BE])
        
        return chosen_BS, chosen_BE, path_NPT, path_PT
    
    def twoway_bridge_twoway(self, A):
        #Allow BS or J to be chosen for F
        Fs = self.BS
        Fs.extend(self.J)
        
        chosen_A, chosen_F, path_AF = create_bridge_twoway(G = self.TW, As = [A], Fs = Fs)
        
        path_graph.update_other_G(self.TW, [self.OW_NPT, self.OW_PT])
        
        #dont sync F bc it has not been finalized
        #DO sync A to BS, BE bc we just chose it
        sync_base_room_lists(chosen_A, [self.BS, self.BE])
        
        return chosen_A, chosen_F, path_AF
    
    def get_matching_J_BS(self, initial_room):
        
        #get branch door or only door from initial_room
        #find J whose only and BS whose branch match that door type and dir
        #include initial room in the lists
        
        door_to_match = None
        valid_rooms = []
        valid_johns = []
        
        if isinstance(initial_room, BranchRoom):
            door_to_match = initial_room.branch_door
            valid_rooms.append(initial_room)
        else:
            door_to_match = initial_room.door
            valid_johns.append(initial_room)
        
        for potential_room in self.BS:
            
            if match_door(door_to_match, potential_room.branch_door):
                valid_rooms.append(potential_room)
        
        for potential_room in self.J:
            if match_door(door_to_match, potential_room.door):
                valid_johns.append(potential_room)
        
        return valid_rooms, valid_johns
    
    def get_matching_JBE_BE(self, initial_room):
        
        #get branch door or only door from initial_room
        #find J whose only and BS whose branch match that door type and dir
        #include initial room in the lists
        
        valid_rooms = []
        valid_johns = []
        
        PT_match = initial_room.PT_door
        NPT_match = initial_room.NPT_door
        
        if isinstance(initial_room, BranchRoom):
            valid_rooms.append(initial_room)
        else:
            valid_johns.append(initial_room)
        
        for potential_room in self.BE:
            
            if match_door(PT_match, potential_room.PT_door) and match_door(NPT_match, potential_room.NPT_door):
                valid_rooms.append(potential_room)
        
        for potential_room in self.JBE:
            
            if match_door(PT_match, potential_room.PT_door) and match_door(NPT_match, potential_room.NPT_door):
                valid_johns.append(pot)
        
        return valid_rooms, valid_johns

    #TODO TODO:
    #sync base room lists actually removed room from sync and from self
    #so this is unncessary?
    #but this might be cleaner
    #and we need the refund system too

    def get_viable_entrance(self, seg):
        chosen_room = seg.get_viable_room()
        
        if isinstance(room, EntranceRoom):
            self.E.remove(chosen_room)
            return chosen_room
        elif isinstance(room, EJBranchRoom):
            self.EBS.remove(chosen_room)
            return chosen_room
        else:
            raise RuntimeError("got room that wasnt in E or EBS")
    
    def refund_entrance(self, room):
        if isinstance(room, EntranceRoom):
            self.E.append(room)
        elif isinstance(room, EJBranchRoom):
            self.EBS.append(room)
        else:
            raise RuntimeError("refund room that wasnt in E or EBS")

    def get_viable_branch_start(self, seg):
        chosen_room = seg.get_viable_room()
        
        if isinstance(room, BranchRoom):
            self.BS.remove(chosen_room)
            return chosen_room
        else:
            raise RuntimeError("got room that wasnt in BS")
    
    def refund_branch_start(self, room):
        if isinstance(room, BranchRoom):
            self.BS.append(room)
        else:
            raise RuntimeError("refund room that wasnt in BS")
    
    def get_viable_branch_end(self, seg):
        chosen_room = seg.get_viable_room()
        
        if isinstance(room, BranchRoom):
            self.BE.remove(chosen_room)
            return chosen_room
        else:
            raise RuntimeError("got room that wasnt in BE")
    
    def refund_branch_end(self, room):
        if isinstance(room, BranchRoom):
            self.BE.append(room)
        else:
            raise RuntimeError("refund room that wasnt in BE")

def match_door(door, other):
    return door.door_type == other.door_type and door.door_dir == other.door_dir

def create_level(TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE)

    level = Level()
    layers = Layers(TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE)
    
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
            successful = add_entrance_segments(level, layers, last_room_seg)
            
            #If Failed, level is fail!
            if not successful:
                return None

        elif last_room_seg.is_branch_end:
            #Bridge Twoway from last branch to new branch or J if none
            successful, john_end = add_twoway_segments(level, TW, OW_NPT, OW_PT, BS, BE, last_room_seg)
        else:
            #Create branch segment to BE or JBE if none
            successful, john_end = add_branch_segments(level, layers, last_room_seg)
        
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
    
    #TODO TODO: refund removed segments, sync with layers

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
            chosen_A, chosen_F, path_AF = layers.entrance_bridge_twoway(chosen_room)
            
            if chosen_F is None:
                layers.refund_entrance(chosen_A)
                continue
            
            valid_rooms, valid_johns = layers.get_matching_J_BS(chosen_A)
            add_path_to_level(level, path_AF, valid_rooms, valid_johns)
            
            return True
            
        else:
            chosen_BS, chosen_BE, path_NPT, path_PT = layers.entrance_bridge_oneway(chosen_room)
            
            if chosen_BE is None:
                layers.refund_entrance(chosen_BS)
                continue
            
            valid_rooms, valid_johns = layers.get_matching_JBE_BE(chosen_BS)
            add_branch_to_level(level, path_NPT, path_PT, valid_rooms, valid_johns)
            
            return True

def add_branch_segments(level, layers, last_room_seg):
    #create oneway bridge: last_room_seg (viable BSs) > OW > BE/JBE
    #or
    #choose J from last_room_seg
    
    while True:
        
        chosen_room = layers.get_viable_branch_start(last_room_seg) #also sets
            
        if chosen_room is None:
            break #try john
        
        #dont sync BE bc it has not been finalized
        #DO sync BS to BS, BE bc we just chose it
        chosen_BS, chosen_BE, path_NPT, path_PT = layers.branch_bridge_oneway(chosen_room)
        
        if chosen_BE is None:
            refund_branch_start(chosen_BS)
            continue
        
        valid_rooms, valid_johns = layers.get_matching_JBE_BE(chosen_BS)
        add_branch_to_level(level, path_NPT, path_PT, valid_rooms, valid_johns)
        
        return True, False #success but not john
    
    while True:
        chosen_room = last_room_seg.get_viable_john_room() #also sets 
            
        if chosen_room is None:
            return False, False #Failed!
            
        #dont add to level because last_room_seg.get already set chosen room
        
        return True, True #success and john


def add_twoway_segments(level, layers, last_room_seg):
    #create oneway bridge: last_room_seg (viable BSs) > OW > BE/JBE
    #or
    #choose J from last_room_seg
    
    while True:
        
        #get room and sync
        chosen_room = layers.get_viable_branch_end(last_room_seg) #also sets
            
        if chosen_room is None:
            break #try john
        
        chosen_A, chosen_F, path_AF = layers.twoway_bridge_twoway(chosen_room)
        
        if chosen_F is None:
            layers.refund_branch_end(chosen_A)
            continue
        
        valid_rooms, valid_johns = layers.get_matching_J_BS(chosen_A)
        add_path_to_level(level, path_AF, valid_rooms, valid_johns)
        
        return True, False #success but not john
    
    while True:
        chosen_room = last_room_seg.get_viable_john_room() #also sets
            
        if chosen_room is None:
            return False, False #Failed!
            
        #dont add to level because last room seg.get already set
        
        return True, True #success and john
















