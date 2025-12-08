import * from enums
import networkx as nx

#==========================================
#   Layer Creation
#==========================================
#All Rooms
#Divide into room types for different layers
def rooms_to_layers(rooms):
    
    TW_start_layer, TW_exit_layer, OW_start_layer, OW_exit_layer = rooms_to_TW_and_OW_layers(rooms):
    branch_start_layer, branch_end_layer = rooms_to_branch_layers(rooms)
    john_layer, branch_john_layer = rooms_to_john_layer(rooms)
    entrance_layer, branch_entrance_layer = rooms_to_entrance_layer(rooms)
    
    return

#RoomType.NORMAL
#Four Copies, one with and one without oneway paths
#One layer for starts one layer for exits
def rooms_to_TW_and_OW_layers(rooms):
    
    normal_rooms = filter_rooms(rooms, RoomType.NORMAL)
    
    return

#RoomType.BRANCH
#Two layers
def rooms_to_branch_layers(rooms):
    return

#BranchType.START or BranchType.ANY
def rooms_to_branch_start_layer(rooms):
    return

#BranchType.END or BranchType.ANY
def rooms_to_branch_end_layer(rooms):
    return

#RoomType.JOHN
def rooms_to_john_layer(rooms):
    return

#RoomType.ENTRANCE
def rooms_to_entrance_layer(rooms):
    return

def filter_rooms(rooms, room_type):
    new_rooms = [room for room in rooms if room.roomtype == room_type]

#==========================================
#   Layer Connection
#==========================================

def connect_start_exit_layers(start_layer, exit_layer):
    return




















