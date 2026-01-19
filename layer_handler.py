from path_traversal import create_bridge_twoway, create_bridge_oneway
from path_graph import update_other_G
from layer_objects import EntranceRoom, JohnRoom, EJBranchRoom, BranchRoom

#store and manage synchronization of layers
#all requests for paths from layers should be
#done through this class
def match_door(door, other):
    return door.door_type == other.door_type and door.door_dir == other.door_dir


class LayerHandler():
    
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
        self.BS_removed = []
        self.BE_removed = []

    def bridge_twoway(self, A):
        #Allow BS or J to be chosen for F
        Fs = []
        Fs.extend(self.BS)
        Fs.extend(self.J)
        
        chosen_A, chosen_F, path_AF = create_bridge_twoway(G = self.TW, As = [A], Fs = Fs)
        
        if chosen_F is not None:
            update_other_G(self.TW, [self.OW_NPT, self.OW_PT])
        
        return chosen_A, chosen_F, path_AF
    
    def bridge_oneway(self, A):
        #Allow BE or JBE to be chosen for BE
        BEs = []
        BEs.extend(self.BE)
        BEs.extend(self.JBE)
        
        chosen_BS, chosen_BE, path_NPT, path_PT = create_bridge_oneway(G_NPT = self.OW_NPT, G_PT = self.OW_PT, BSs = [A], BEs = BEs) 
        
        if chosen_BE is not None:
            update_other_G(self.OW_NPT, [TW])
            update_other_G(self.OW_PT, [TW])
        
        return chosen_BS, chosen_BE, path_NPT, path_PT
    

        return chosen_BS, chosen_BE, path_NPT, path_PT
    
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

    def get_viable_entrance(self, seg):
        chosen_room = seg.get_viable_room() #TODO: for some reason its putting in johns in here
        
        if chosen_room is None:
            return None
        
        print("Try get type of ", str(type(chosen_room)))
        print(chosen_room.__class__, id(chosen_room.__class__))
        print(EJBranchRoom, id(EJBranchRoom))
        
        print("is ER: ", isinstance(chosen_room, EntranceRoom))
        print("is EBR: ", isinstance(chosen_room, EJBranchRoom))
        
        if isinstance(chosen_room, EntranceRoom):
            self.E.remove(chosen_room)
            return chosen_room
        elif isinstance(chosen_room, EJBranchRoom):
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
        
        if chosen_room is None:
            return None
        
        if isinstance(chosen_room, BranchRoom):
            self.BS.remove(chosen_room)
            self.BS_removed.append(chosen_room)
            
            #sync with BE
            self.sync(chosen_room, self.BE, self.BE_removed)
            
            return chosen_room
        else:
            raise RuntimeError("got room that wasnt in BS")
    
    def refund_branch_start(self, room):
        if isinstance(room, BranchRoom):
            self.BS.append(room)
            self.BS_removed.remove(room)
            
            #sync with BE
            self.sync(room, self.BE_removed, self.BE)
            
        else:
            raise RuntimeError("refund room that wasnt in BS")
    
    #if room is in list that should have it
    #remove it and add it to the other
    def sync(self, sync_room, other_remove_from, other_append_to):
        for other_room in other_remove_from:
            if other_room.room_name == sync_room.room_name:
                other_remove_from.remove(other_room)
                other_append_to.append(other_room)
                break
    
    def get_viable_branch_end(self, seg):
        chosen_room = seg.get_viable_room()
        
        if chosen_room is None:
            return None
        
        if isinstance(chosen_room, BranchRoom):
            self.BE.remove(chosen_room)
            self.BE_removed.append(chosen_room)
            
            #sync with BS
            self.sync(chosen_room, self.BS, self.BS_removed)
            
            return chosen_room
        else:
            raise RuntimeError("got room that wasnt in BE")
    
    def refund_branch_end(self, room):
        if isinstance(room, BranchRoom):
            self.BE.append(room)
            self.BE_removed.remove(room)
            
            #sync with BS
            self.sync(room, self.BS_removed, self.BS)
            
        else:
            raise RuntimeError("refund room that wasnt in BE")
    
    def get_viable_john(self, seg):
        
        chosen_room = seg.get_viable_john()
        
        if chosen_room is None:
            return None
        
        if isinstance(chosen_room, JohnRoom):
            self.J.remove(chosen_room)
        elif isinstance(chosen_room, EJBranchRoom):
            self.JBE.remove(chosen_room)
        else:
            raise RuntimeError("get john that wasnt in J or JBE")