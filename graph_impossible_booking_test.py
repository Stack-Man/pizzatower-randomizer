#Author: Stack Man
#Date: 11/7/2026

#Test impossible booking by creating graphs that are forced through multiple DB edges

from objects import Door, Path, Room
from graph_objects import PathEdge, DoorNode
from enums import DoorType, DoorDir, PathTime, AccessType, StartExitType, RoomType, TraversalType
import networkx as nx
from graph_impossible_booking import add_to_bipartite_graph

def test_2_edges_1_room():

    path_AB, door_A, door_B = oneway_path("A", "B", DoorType.A, DoorType.B)
    path_CD, door_C, door_D = oneway_path("C", "D", DoorType.C, DoorType.D)

    path_AB.is_double_bookable = True
    path_CD.is_double_bookable = True

    room_AB_CD = Room("room_AB_CD", [door_A, door_B, door_C, door_D], [path_AB, path_CD], False, False, False, False)

    room_AB_CD.is_double_bookable = True
    room_AB_CD.room_type = RoomType.NORMAL

    edge_AB = edge_from_doors(door_A, door_B)
    edge_CD = edge_from_doors(door_C, door_D)

    bipartite_TW = nx.Graph()
    bipartite_PT = nx.Graph()
    bipartite_NPT = nx.Graph()

    edge_AB.set_paths([path_AB], [], [], [])
    edge_CD.set_paths([path_CD], [], [], [])

    add_to_bipartite_graph(bipartite_TW, bipartite_PT, bipartite_NPT, TraversalType.ANY, edge_AB)
    _, TW, PT, NPT = add_to_bipartite_graph(bipartite_TW, bipartite_PT, bipartite_NPT, TraversalType.ANY, edge_CD) #should incur impossible booking

    return TW, PT, NPT

def test_2_edges_2_rooms():
    path_AB, door_A, door_B = oneway_path("A", "B", DoorType.A, DoorType.B)
    path_CD, door_C, door_D = oneway_path("C", "D", DoorType.C, DoorType.D)

    path_AB.is_double_bookable = True
    path_CD.is_double_bookable = True

    room_AB = Room("room_AB", [door_A, door_B], [path_AB], False, False, False, False)
    room_CD = Room("room_CD", [door_C, door_D], [path_CD], False, False, False, False)

    room_AB.is_double_bookable = True
    room_AB.room_type = RoomType.NORMAL

    room_CD.is_double_bookable = True
    room_CD.room_type = RoomType.NORMAL

    edge_AB = edge_from_doors(door_A, door_B)
    edge_CD = edge_from_doors(door_C, door_D)

    bipartite_TW = nx.Graph()
    bipartite_PT = nx.Graph()
    bipartite_NPT = nx.Graph()

    edge_AB.set_paths([path_AB], [], [], [])
    edge_CD.set_paths([path_CD], [], [], [])

    add_to_bipartite_graph(bipartite_TW, bipartite_PT, bipartite_NPT, TraversalType.ANY, edge_AB)
    _, TW, PT, NPT = add_to_bipartite_graph(bipartite_TW, bipartite_PT, bipartite_NPT, TraversalType.ANY, edge_CD) #should NOT incur impossible booking

    return TW, PT, NPT

def test_2_edges_2_rooms_then_2_edges_1_room():
    path_AB, door_A, door_B = oneway_path("A", "B", DoorType.A, DoorType.B)
    path_CD, door_C, door_D = oneway_path("C", "D", DoorType.C, DoorType.D)

    path_AB.is_double_bookable = True
    path_CD.is_double_bookable = True

    room_AB = Room("room_AB", [door_A, door_B], [path_AB], False, False, False, False)
    room_CD = Room("room_CD", [door_C, door_D], [path_CD], False, False, False, False)

    room_AB.is_double_bookable = True
    room_AB.room_type = RoomType.NORMAL

    room_CD.is_double_bookable = True
    room_CD.room_type = RoomType.NORMAL

    edge_AB = edge_from_doors(door_A, door_B)
    edge_CD = edge_from_doors(door_C, door_D)



    edge_AB.set_paths([path_AB], [], [], [])
    edge_CD.set_paths([path_CD], [], [], [])



    #Add a disconnected component that causes an invalid booking
    path_AB2, door_A2, door_B2 = oneway_path("A2", "B2", DoorType.A2, DoorType.B2)
    path_CD2, door_C2, door_D2 = oneway_path("C2", "D2", DoorType.C2, DoorType.D2)

    path_AB2.is_double_bookable = True
    path_CD2.is_double_bookable = True

    room_AB_CD = Room("room_AB_CD", [door_A2, door_B2, door_C2, door_D2], [path_AB2, path_CD2], False, False, False, False)

    room_AB_CD.is_double_bookable = True
    room_AB_CD.room_type = RoomType.NORMAL

    edge_AB2 = edge_from_doors(door_A2, door_B2)
    edge_CD2 = edge_from_doors(door_C2, door_D2)

    edge_AB2.set_paths([path_AB2], [], [], [])
    edge_CD2.set_paths([path_CD2], [], [], [])

    bipartite_TW = nx.Graph()
    bipartite_PT = nx.Graph()
    bipartite_NPT = nx.Graph()

    add_to_bipartite_graph(bipartite_TW, bipartite_PT, bipartite_NPT, TraversalType.ANY, edge_AB)
    add_to_bipartite_graph(bipartite_TW, bipartite_PT, bipartite_NPT, TraversalType.ANY, edge_CD) #should NOT incur impossible booking
    add_to_bipartite_graph(bipartite_TW, bipartite_PT, bipartite_NPT, TraversalType.ANY, edge_AB2) # Still valid bc disconnected component R=E
    _, TW, PT, NPT = add_to_bipartite_graph(bipartite_TW, bipartite_PT, bipartite_NPT, TraversalType.ANY, edge_CD2) #should incur impossible booking

    return TW, PT, NPT


def edge_from_doors(a: Door, b: Door):
    door_A_node = DoorNode(a.door_type, a.door_dir, StartExitType.START)
    door_B_node = DoorNode(b.door_type, b.door_dir, StartExitType.EXIT)
    edge_AB = PathEdge(door_A_node, door_B_node)

    return edge_AB

def oneway_path(a: str, b: str, type_a: DoorType, type_b: DoorType):
    door_A = Door(a, type_a, DoorDir.NONE, False, False, False, False, PathTime.BOTH, AccessType.STARTONLY, PathTime.BOTH, False, False)
    door_B = Door(b, type_b, DoorDir.NONE, False, False, False, False, PathTime.BOTH, AccessType.EXITONLY, PathTime.BOTH, False, False)
    
    path_AB = Path(door_A, door_B, True, False)

    return path_AB, door_A, door_B

TW, PT, NPT = test_2_edges_1_room()

#Assert all are impossible = True
assert(TW == True)
assert(PT == True)
assert(NPT == True)

