#Author: Stack Man
#Date: 11/11/2026

#get a traversal between a two room paths from FG

from level_objects import BaseRoomPath, RoomPath, BranchRoomPath
from enums import TraversalType, StartExitType
from graph_from_rooms import FlowGraphHandler
from level_clean_traversal import clean_depleted_traverals
from graph_objects import DoorNode, CombinedDoorNode

import networkx as nx

LOGGING = True

def log(msg: str):
    if (LOGGING):
        print(msg)

def get_traversal(srp: BaseRoomPath, erp: BaseRoomPath, FG: FlowGraphHandler, traversal_type: TraversalType):
    #connect start rp's end to end rp's start
    #convert srp and erp into DoorNodes to search FG with

    source = get_path_end(srp, traversal_type)
    destination = get_path_start(erp, traversal_type)

    log(f"get_traversal: Got SD from {source} to {destination}")

    FG = clean_depleted_traverals(FG)

    log(f"get_traversal: clean_depleted_traverals()")

    traversals = get_traversals_between(FG, source, destination)

    log(f"get_traversal: Trying from {len(traversals)} traversals ")

    for traversal in traversals:
        if (traversal.traversal_type == traversal_type and traversal.has_no_zero_edges()):
            log(f"get_traversal: Got traversal {traversal} ")
            return traversal

        log(f"get_traversal: invalid traversal {traversal} of type {traversal.traversal_type}, wanted {traversal_type}. has no zero edges: {traversal.has_no_zero_edges()}")

    raise RuntimeError(f"No traversal of {traversal_type} between {source} and {destination}")

def get_traversals_between(FG: FlowGraphHandler, source: DoorNode, destination: DoorNode ):
    for N in FG.nodes():

        N: DoorNode | CombinedDoorNode
        if source == N:

            log(f"get_traversals_between found source {N}")

            if destination in N.steps:
                return N.steps[destination]
            else:
                break 

    raise RuntimeError(f"No traversal between {source} and {destination}")

def get_path_end(rp: BaseRoomPath, traversal_type:TraversalType):
    match traversal_type:
        case TraversalType.ANY:
            return get_path_end_TW(rp)
        case _:
            raise NotImplementedError(f"get_path_end() not implemented for {traversal_type}")

def get_path_start(rp: BaseRoomPath, traversal_type: TraversalType):
    match traversal_type:
        case TraversalType.ANY:
            return get_path_start_TW(rp)
        case _:
            raise NotImplementedError(f"get_path_start() not implemented for {traversal_type}")

def get_path_end_TW(rp: BaseRoomPath):
    if (type(rp) == RoomPath):
        t = rp.path.exit_door.get_type_as_tuple()
        return DoorNode(t[0], t[1], StartExitType.EXIT)
    elif (type(rp) == BranchRoomPath):
        t = rp.branch_door.get_type_as_tuple()
        return DoorNode(t[0], t[1], StartExitType.EXIT) 

    raise TypeError(f"RP {rp.room} is not RoomPath or BranchRoomPath")

def get_path_start_TW(rp: BaseRoomPath):
    if (type(rp) == RoomPath):
        t = rp.path.start_door.get_type_as_tuple()
        return DoorNode(t[0], t[1], StartExitType.START)
    elif (type(rp) == BranchRoomPath):
        t = rp.branch_door.get_type_as_tuple()
        return DoorNode(t[0], t[1], StartExitType.START) 

    raise TypeError(f"RP {rp.room} is not RoomPath or BranchRoomPath")