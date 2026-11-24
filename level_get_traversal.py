#Author: Stack Man
#Date: 11/11/2026

#get a traversal between a two room paths from FG

from level_objects import BaseRoomPath, RoomPath, BranchRoomPath
from enums import TraversalType, StartExitType, DoorType
from graph_create import FlowGraphHandler
from graph_objects import DoorNode, CombinedDoorNode, EdgeTraversal, TransitionEdge, PathEdge
from level_clean_replenish import update_traversal_type
from graph_impossible_booking import add_to_bipartite_graph

import logging as log
from colors import ERROR, RESET

def get_traversal(srp: BaseRoomPath, erp: BaseRoomPath, FG: FlowGraphHandler, traversal_type: TraversalType, force_extension: bool = False):

    #connect start rp's end to end rp's start
    #convert srp and erp into DoorNodes to search FG with

    source = get_path_end(srp, traversal_type)
    destination = get_path_start(erp, traversal_type)

    traversals = get_traversals_between(FG, source, destination)

    for traversal in traversals:

        #we deferred updating the traversal type until we actually
        #tried to access it
        update_traversal_type(traversal)
        
        if (good_traversal_type(traversal.traversal_type, traversal_type) and traversal.has_no_zero_edges()):

            #traversal must be longer than one edge (direct connection) if 
            #we are forcing extension. used for growth

            #TODO: if a direct connection, we can add a room by repeating the path type and he dierct connection twice
            #traversals specifically ignore this, how to handle it?

           

            if  (not force_extension) or (force_extension and len(traversal) > 1):
                return traversal
            elif (force_extension and len(traversal) == 1):
                #if a direct connection, we can add a room by repeating the direct connection twice
                #example A--B extends to A--B==A--B
                repeat_traversal = repeat_direct_connection(FG, traversal)

                #log.debug("Trying repeat traversal")

                try:
                    if (good_traversal_type(repeat_traversal.traversal_type, traversal_type) and repeat_traversal.has_no_zero_edges()):
                        #log.debug(f"Used repeat traversal: {repeat_traversal}")
                        return repeat_traversal
                except RuntimeError as e:
                    pass
                    #log.debug(e)

                #log.debug("Failed repeat traversal")

            #bad traversal and no repeat traversal
            #try next


    raise RuntimeError(f"No traversal of {traversal_type} between {source} and {destination}")

def repeat_direct_connection(FG: FlowGraphHandler, direct_traversal: EdgeTraversal):
    direct_edge = direct_traversal.edges[0]

    if (type(direct_edge) != TransitionEdge):
        raise TypeError(f"Direct Edge in repeat_direct_connection was not TransitionEdge but {type(direct_edge)}")

    source = direct_edge.start_node
    destination = direct_edge.end_node

    #reverse S and D so we get the path edge instead of the transition edge
    edge = FG.get_edge_data(destination, source)
    
    #edge may not exist
    if (edge is not None):
        path_edge : PathEdge = edge["object"]

        #log.debug("Repeating with %s to %s to %s", direct_edge, path_edge, direct_edge)

        #have to manually add all of the edges to the traversal
        new_traversal = EdgeTraversal([direct_edge, path_edge, direct_edge])

        #use ANY as starting point for traversal check
        #only adds to BG not to traversal itself, so we add path-edge to traversal manually
        add_to_bipartite_graph(new_traversal.bipartiteTW, new_traversal.bipartitePT, new_traversal.bipartiteNPT, TraversalType.ANY, path_edge)

        return new_traversal
    
    else:
    
        raise RuntimeError(f"No edge of type {destination} to {source}")

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
            raise NotImplementedError(f"good_traversal_type not implemented for {wanted}")

def get_traversals_between(FG: FlowGraphHandler, source: DoorNode, destination: DoorNode ):
    for N in FG.nodes():

        N: DoorNode | CombinedDoorNode
        if source in N: #use IN so Combined node works too

            #use iteration so we ca ncheck if destination is 
            #within a possible combined node K
            for K, V in N.steps.items():
                if destination in K:
                    return V

            raise RuntimeError(f"No traversal between {source} and {destination}")

    raise LookupError(f"{source} was not in FG!")

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

        if (t[0] == DoorType.LEVELDOOR):
            raise ValueError(f"end door of {rp.room} was LevelDoor with traversal type {traversal_type}")

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

        if (t[0] == DoorType.LEVELDOOR):
            raise ValueError(f"start door of {rp.room} was LevelDoor with traversal type {traversal_type}")

        return DoorNode(t[0], t[1], StartExitType.START)
    else:
        raise TypeError(f"RP {rp.room} is not RoomPath or BranchRoomPath")



   