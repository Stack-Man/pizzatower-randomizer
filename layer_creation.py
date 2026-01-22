from enums import *
import networkx as nx
import node_id_objects as nio
from node_id_objects import StartExitType, NodeType
from layer_objects import BranchRoom, EntranceRoom, JohnRoom, EJBranchRoom
from path_graph import layer_to_endpoints

"""
------------------------
STRUCTURE OF LAYER GRAPH
------------------------
The graph consists of 4 "levels"

1. Transition, Start
2. Door, Start
3. Door, Exit
4. Transition, Exit

Two copies of each Transition type and Door letter exist, labeled either Start or Exit
This creates a distinct flow from a Transition > Door > Door > Transition
prventing unwanted backtracking.

Transition Start > Door Start and Door Exit > Transition Exit edges mark a door as that type of transition
Door Start > Door Exit edges represent a path in that room between those two doors

---------------------------
STRUCTURE OF BRANCH "LAYER"
---------------------------
A branch layer is just a list of BranchRoom
each BranchRoom contains the room name and three Endpoint() and Door() for the branch, NPT, and PT doors
These three endpoints are used to coordinate the construction of the paths between branches in layer_traversal
"""
use_loop_paths = False

def rooms_to_layers(rooms, use_loops = False):
    
    use_loop_paths = use_loops
    
    TW, OW_NPT, OW_PT = rooms_to_TW_and_OW_layers(rooms)
    BS, BE = rooms_to_branch_layers(rooms)
    J, JBE = rooms_to_john_layer(rooms)
    E, EBS = rooms_to_entrance_layer(rooms)
    
    #TW and OW should be endpoint graphs, rest are lists of BaseRoom
    TW = layer_to_endpoints(TW)
    OW_NPT = layer_to_endpoints(OW_NPT)
    OW_PT = layer_to_endpoints(OW_PT)
    
    TW.name = "TW"
    OW_NPT.name = "OW_NPT"
    OW_PT.name= "OW_PT"
    
    return TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE

def rooms_to_layer(rooms, path_selector = lambda e: True):
    return populate_start_and_exit_layer(rooms, path_selector)

def rooms_to_base_room_layer(rooms, se_type):
    
    base_rooms = []
    
    for room in rooms:
        
        door = get_non_loop_door(room)
        
        if se_type == StartExitType.EXIT: #EXIT is entrance
            er = EntranceRoom(room.name, door)
            base_rooms.append(er)
        else: #START is john
            jr = JohnRoom(room.name, door)
            base_rooms.append(jr)
    
    return base_rooms

from enums import *

def get_non_loop_door(room):
    
    for door in room.doors:
        if door.door_type is not DoorType.LEVELDOOR and not door.is_loop:
            return door

def rooms_to_branch_layer(rooms, se_type):
    branch_rooms = []

    for room in rooms:
        branch_door = None
        NPT_door = None
        PT_door = None

        #add paths between layers
        for path in room.paths:
            #print("Trying path " + str(path) )
            
            if se_type == StartExitType.START: #branch start
                
                if path.start_door.is_branch: #branch to NPT
                    branch_door = path.start_door
                    
                    if path.exit_door.exit_path_time == PathTime.NOTPIZZATIME:
                        NPT_door = path.exit_door
                    
                elif path.exit_door.is_branch: #PT to branch
                    branch_door = path.exit_door
                    
                    if path.start_door.start_path_time == PathTime.PIZZATIME or path.start_door.access_type == AccessType.STARTONLY:
                        PT_door = path.start_door
                
                
            else: #branch end
                
                if path.exit_door.is_branch: #NPT to branch
                    branch_door = path.exit_door
                    
                    if path.start_door.start_path_time == PathTime.NOTPIZZATIME or path.start_door.access_type == AccessType.STARTONLY:
                        NPT_door = path.start_door
                    
                elif path.start_door.is_branch: #branch to PT
                    branch_door = path.start_door
                    
                    if path.exit_door.exit_path_time == PathTime.PIZZATIME:
                        PT_door = path.exit_door
        
        #create branch room
        if branch_door is not None and NPT_door is not None and PT_door is not None:
            branch_room = BranchRoom(room.name, se_type, branch_door, NPT_door, PT_door)
            branch_rooms.append(branch_room)
        else:
            print("=====ROOM ", room.name, " NOT VALID BRANCH (MISSING DOOR)")
    
    return branch_rooms

def rooms_to_ej_branch_layer(rooms, se_type):
    branch_rooms = []

    for room in rooms:
        NPT_door = None
        PT_door = None

        #add paths between layers
        for path in room.paths:
            #print("Trying path " + str(path) )
            
            if path.exit_door.exit_path_time == PathTime.PIZZATIME:
                PT_door = path.exit_door
            elif path.exit_door.exit_path_time == PathTime.NOTPIZZATIME:
                NPT_door = path.exit_door
                
            if path.start_door.start_path_time == PathTime.PIZZATIME:
                PT_door = path.start_door
            elif path.start_door.start_path_time == PathTime.NOTPIZZATIME:
                NPT_door = path.start_door
    
        #create branch room
        if NPT_door is not None and PT_door is not None:
            branch_room = EJBranchRoom(room.name, se_type, NPT_door, PT_door)
            branch_rooms.append(branch_room)
        else:
            print("=====ROOM ", room.name, " NOT VALID BRANCH (MISSING DOOR)")
    
    return branch_rooms

#start/exit layers are virtual layers within a single greater layer
#each door exists twice in the layer, once in start and once in exit
#providing a way to create distinct directionality as you move through the
#layer and preventing unwanted backtracking
"""
---------------------------------
ALGORITHM - CONSTRUCT LAYER GRAPH
---------------------------------
Assume we have an already filtered list of rooms

1. For every room R
2.      For every door letter D in R
3.          Add R_D to G
4.      For every path P in R
5.          Add edge R_P to G

3b. Add R_D as R_D_START and R_D_EXIT

5b. Add P_START and P_EXIT (P_S/P_E, P_door_type, P_dir) type to G as Transition Nodes
5c. Add R_P as (R_D_START, R_D_EXIT)
5d. Add reverse of 5b and 5c if P is not oneway

"""
def populate_start_and_exit_layer(rooms, path_selector = lambda e: True):
    global use_loop_paths
    
    layer = nx.DiGraph()
    layer_ids = [StartExitType.START, StartExitType.EXIT]

    for room in rooms:
        room_id = nio.create_room_node_id(room.name)

        layer.add_node(room_id)
       
        for door in room.doors:
            
            #add door and connect room to door
            for layer_type_id in layer_ids:
                
                #Layer name, start/exit, room name, door letter
                door_id = nio.create_door_node_id(layer_type_id, room.name, door.letter)
                
                layer.add_node(door_id)
                layer.add_edge(room_id, door_id)    

        #add paths between layers
        for path in room.paths:
            #print("Trying path " + str(path) )
            
            valid_loop = not path.is_loop or (path.is_loop and use_loop_paths)
            valid_path = path_selector(path) and valid_loop
            
            if valid_path:
                #print("valid path " + str(path) + " vp " + str(valid_path))
                add_start_exit_path_to_layer(room.name, path, layer)
            #else:
                #print("invalid path " + str(path)  + " vp " + str(valid_path))
    
    return layer

#add path and reverse if not oneway
def add_start_exit_path_to_layer(room_name, path, layer):
    
    add_one_start_exit_path_to_layer(room_name, path, path.start_door, path.exit_door, layer)
    
    #only allow start > exit if oneway or initially blocked on either side
    if not path.oneway and not path.start_door.initially_blocked and not path.exit_door.initially_blocked:
        add_one_start_exit_path_to_layer(room_name, path, path.exit_door, path.start_door, layer)
    
    return
    
def add_one_start_exit_path_to_layer(room_name, path, start_door, exit_door, layer):
    #add start transition node
    #Layer name, start/exit, door type, door direction
    start_transition_id = nio.create_transition_node_id(StartExitType.START, start_door.door_type, start_door.door_dir)
    layer.add_node(start_transition_id)
    
    #add exit transition node
    exit_transition_id = nio.create_transition_node_id(StartExitType.EXIT, exit_door.door_type, exit_door.door_dir)
    layer.add_node(exit_transition_id)
    
    #connect start transition type to start door in start layer
    #add path as attribute to this edge
    
    #Layer name, start/exit, room name, door letter
    start_door_id = nio.create_door_node_id(StartExitType.START, room_name, start_door.letter)
    layer.add_edge(start_transition_id, start_door_id) 
    
    #connect exit door to exit transition type to in exit layer
    exit_door_id = nio.create_door_node_id(StartExitType.EXIT, room_name, exit_door.letter)
    layer.add_edge(exit_door_id, exit_transition_id)
    
    #connect start door in start layer to exit door in exit layer
    layer.add_edge(start_door_id, exit_door_id)
    
    #add path object to that edge
    layer[start_door_id][exit_door_id]["path"] = path
    
    return


#RoomType.NORMAL
#Two layers, one with and one without oneway paths
def rooms_to_TW_and_OW_layers(all_rooms):
    rooms = filter_rooms(all_rooms, RoomType.NORMAL)

    #paths cant be oneway
    #and have to be traversible both ways in different times
    def valid_path_for_two_way_layer(path):
        a = not path.oneway
        
        #TODO: doesnt cover ratblocked doors
        
        b = path.start_door.start_path_time == PathTime.BOTH or path.start_door.initially_blocked
        c = path.start_door.exit_path_time == PathTime.BOTH or path.start_door.initially_blocked
        d = path.exit_door.start_path_time == PathTime.BOTH or path.exit_door.initially_blocked
        e = path.exit_door.exit_path_time == PathTime.BOTH or path.exit_door.initially_blocked
        
        valid = a and b and c and d and e
        
        return valid

    def valid_for_OW_TIME_layer(path, wrong_time):
        a = not path.start_door.start_path_time == wrong_time
        b = not path.exit_door.start_path_time == wrong_time
        c = not path.start_door.exit_path_time == wrong_time
        d = not path.exit_door.exit_path_time == wrong_time
        
        valid = a and b and c and d
        
        #print("path: " + str(path) + " wrong_time: " + str(wrong_time) + " a, b, c, d: " + str(path.start_door.start_path_time) + ", "+ str(path.exit_door.start_path_time) + ", "+ str(path.start_door.exit_path_time) + ", "+ str(path.exit_door.exit_path_time) )
        #print(" vp: " + str(valid) + " a, b, c, d: " + str(a) + ","+ str(b) + ","+ str(c) + ","+ str(d))
        
        return valid
    
    def valid_for_OW_NPT_layer(path):
        return valid_for_OW_TIME_layer(path, wrong_time = PathTime.PIZZATIME)
    
    def valid_for_OW_PT_layer(path):
        return valid_for_OW_TIME_layer(path, wrong_time = PathTime.NOTPIZZATIME)
    

    TW_layer = rooms_to_layer(rooms, valid_path_for_two_way_layer)
    OW_NPT_layer = rooms_to_layer(rooms, valid_for_OW_NPT_layer)
    OW_PT_layer = rooms_to_layer(rooms, valid_for_OW_PT_layer)
    
    TW_layer.graph["name"] = "Two Way"
    OW_NPT_layer.graph["name"] = "One Way NPT"
    OW_PT_layer.graph["name"] = "One Way PT"
    
    return TW_layer, OW_NPT_layer, OW_PT_layer
    

#RoomType.BRANCH
#Two layers
#   BranchType.START or BranchType.ANY  (start and exit)
#   BranchType.END or BranchType.ANY    (start and exit)

def rooms_to_branch_layers(all_rooms):
    branch_rooms = filter_rooms(all_rooms, RoomType.BRANCH)
    
    print("Filtered branch rooms:   ")
    
    for room in branch_rooms:
        print("     ", room)
    
    B_any_rooms = filter_rooms_by_branch(branch_rooms, BranchType.ANY)
    B_start_rooms = filter_rooms_by_branch(branch_rooms, BranchType.START)
    B_end_rooms = filter_rooms_by_branch(branch_rooms, BranchType.END)
    

    #TODO: BranchType.MID
    
    B_start_rooms.extend(B_any_rooms)
    B_end_rooms.extend(B_any_rooms)
    
    print("Filtered any rooms:   ")
    
    for room in B_any_rooms:
        print("     ", room)
    
    print("Filtered start rooms:   ")
    
    for room in B_start_rooms:
        print("     ", room)
    
    print("Filtered end rooms:   ")
    
    for room in B_end_rooms:
        print("     ", room)
    
    BS_layer = rooms_to_branch_layer(B_start_rooms, StartExitType.START)
    BE_layer = rooms_to_branch_layer(B_end_rooms, StartExitType.EXIT)
    
    #BS_layer.graph["name"] = "Branch Start"
    #BE_layer.graph["name"] = "Branch End"
    
    return BS_layer, BE_layer


#RoomType.JOHN
def rooms_to_john_layer(all_rooms):
    JBE_layer, J_layer = type_and_branch_to_layers(all_rooms, RoomType.JOHN, BranchType.END, StartExitType.EXIT, StartExitType.START)
    
    #JBE_layer.graph["name"] = "John Branch"
    #J_layer.graph["name"] = "John"
    
    return J_layer, JBE_layer 
    

#RoomType.ENTRANCE
def rooms_to_entrance_layer(all_rooms):
    EBS_layer, E_layer = type_and_branch_to_layers(all_rooms, RoomType.ENTRANCE, BranchType.START, StartExitType.START, StartExitType.EXIT)
    
    #EBS_layer.graph["name"] = "Entrance Branch"
    #E_layer.graph["name"] = "Entrance"
    
    return E_layer, EBS_layer
    

def type_and_branch_to_layers(all_rooms, room_type, branch_type, branch_se_type, base_se_type):
    
    type_rooms = filter_rooms(all_rooms, room_type)
    type_branch_rooms = filter_rooms_by_branch(type_rooms, branch_type)
    type_rooms = filter_rooms_by_branch(type_rooms, BranchType.NONE)
    
    TBT_layer = rooms_to_ej_branch_layer(type_branch_rooms, branch_se_type)
    T_layer = rooms_to_base_room_layer(type_rooms, base_se_type)
    
    return TBT_layer, T_layer
    

def filter_rooms(rooms, room_type):
    return [room for room in rooms if room.room_type == room_type]

def filter_rooms_by_branch(rooms, branch_type):
    return [room for room in rooms if room.branch_type == branch_type]






















