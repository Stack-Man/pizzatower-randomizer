#Author: Stack Man
#Date: 11/11/2026

#get a traversal between a two room paths from FG

from level_objects import BaseRoomPath, RoomPath, BranchRoomPath
from enums import TraversalType, StartExitType
from graph_from_rooms import FlowGraphHandler
from level_clean_traversal import clean_depleted_traverals
from graph_objects import DoorNode, CombinedDoorNode

LOGGING = True

from graph_flow_test import print_steps

def log(msg: str):
    if (LOGGING):
        print(msg)

def get_traversal(srp: BaseRoomPath, erp: BaseRoomPath, FG: FlowGraphHandler, traversal_type: TraversalType):
    #connect start rp's end to end rp's start
    #convert srp and erp into DoorNodes to search FG with

    source = get_path_end(srp, traversal_type)
    destination = get_path_start(erp, traversal_type)

    log(f"TRAVERSAL: get_traversal: Got SD from {source} to {destination}")

    FG = clean_depleted_traverals(FG)

    traversals = get_traversals_between(FG, source, destination)

    log(f"TRAVERSAL: get_traversal: Trying from {len(traversals)} traversals ")

    for traversal in traversals:
        if (good_traversal_type(traversal.traversal_type, traversal_type) and traversal.has_no_zero_edges()):
            log(f"      get_traversal: Got traversal {traversal} ")
            return traversal

        log(f"      get_traversal: invalid traversal {traversal} of type {traversal.traversal_type}, wanted {traversal_type}. has no zero edges: {traversal.has_no_zero_edges()}")




    raise RuntimeError(f"TRAVERSAL: No traversal of {traversal_type} between {source} and {destination}")

def good_traversal_type(given: TraversalType, wanted: TraversalType):

    match wanted:
        case TraversalType.ANY:
            return given in [TraversalType.ANY]
        case TraversalType.OW:
            return given in [TraversalType.ANY, TraversalType.OW]
        case TraversalType.NOTPIZZATIME:
            return given in [TraversalType.ANY, TraversalType.OW, TraversalType.NOTPIZZATIME]
        case TraversalType.PIZZATIME:
            return given in [TraversalType.ANY, TraversalType.OW, TraversalType.PIZZATIME]
        case _:
            raise NotImplementedError(f"TRAVERSAL: good_traversal_type not implemented for {wanted}")

def get_traversals_between(FG: FlowGraphHandler, source: DoorNode, destination: DoorNode ):
    for N in FG.nodes():

        N: DoorNode | CombinedDoorNode
        if source == N:

            log(f"TRAVERSAL: get_traversals_between found source {N}")

            if destination in N.steps:
                return N.steps[destination]
            else:
                break 

    log(f"TRAVERSAL: NO TRAVERSAL FOUND")

    print_steps(FG, False)

    raise RuntimeError(f"TRAVERSAL: No traversal between {source} and {destination}")

def get_path_end(rp: BaseRoomPath, traversal_type:TraversalType):
    if (type(rp) == RoomPath):
        t = rp.path.exit_door.get_type_as_tuple()
        return DoorNode(t[0], t[1], StartExitType.EXIT)
    elif (type(rp) == BranchRoomPath):
        door = None

        match traversal_type:
            case TraversalType.ANY:
                door = rp.branch_door
            case TraversalType.NOTPIZZATIME:
                #we get the end type of the Source room
                #for a NPT path this must be the NPT exit
                door = rp.npt.exit_door
            case TraversalType.PIZZATIME:
                door = rp.pt.exit_door
            case TraversalType.OW:
                door = rp.branch_door
            case _:
                raise NotImplementedError(f"get_path_end() not implemented for {traversal_type}")

        t = door.get_type_as_tuple()
        return DoorNode(t[0], t[1], StartExitType.EXIT) 
    else:
        raise TypeError(f"RP {rp.room} is not RoomPath or BranchRoomPath")

def get_path_start(rp: BaseRoomPath, traversal_type: TraversalType):
    if (type(rp) == RoomPath):
        t = rp.path.start_door.get_type_as_tuple()
        return DoorNode(t[0], t[1], StartExitType.START)
    elif(type(rp) == BranchRoomPath):
        door = None

        match traversal_type:
            case TraversalType.ANY:
                door = rp.branch_door
            case TraversalType.NOTPIZZATIME:
                #if NPT, then must be a branch path
                #if a branch path, then we go between two branches, exiting from NPT and entering from NPT
                #when we get start, we get the start of the destination room, so return NPT start
                door = rp.npt.start_door
            case TraversalType.PIZZATIME:
                door = rp.pt.start_door
            case TraversalType.OW:
                #to be OW only it must be outside a branch, therefore
                #a OW path within a TW segment (special case)
                door = rp.branch_door
            case _:
                raise NotImplementedError(f"get_path_start() not implemented for {traversal_type}")

        t = door.get_type_as_tuple()
        return DoorNode(t[0], t[1], StartExitType.START)
    else:
        raise TypeError(f"RP {rp.room} is not RoomPath or BranchRoomPath")



   