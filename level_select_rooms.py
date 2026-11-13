#Author: Stack Man
#Date: 11/11/2026

#select rooms and paths to fill the edges of the traversal

import networkx as nx
from objects import Path, Room
from graph_objects import EdgeTraversal, PathEdge, TransitionEdge, PathList
from level_objects import RoomSelection, RoomPath
from graph_from_rooms import FlowGraphHandler
from enums import TraversalType
from colors import WARNING, RESET

def select_rooms(FG: FlowGraphHandler, traversal: EdgeTraversal, traversal_type: TraversalType):
    print(f"{WARNING}select_rooms does not avoid impossible bookings!{RESET}")

    room_paths : list[RoomPath] = []


    for edge in traversal.edges: #TODO traversal is not prioritizing edges from the bipartite graph with the fewest rooms.. impossible booking may be encountered!

        if (type(edge) == TransitionEdge): #no selection for transition edges
            continue
        elif (type(edge) == PathEdge):
            path, emptied_edge = get_path(edge, traversal_type)

            rp = RoomPath(path.room, path)

            room_paths.append(rp)

            #clean up other paths of consumed room from their respective edges
            if (path.is_double_bookable):
                clean_DB_room(path.room)

            #Store emptied edges in FG
            #FG updates its traversals before access in get_traversal() in level_get_traversal.py
            if (emptied_edge):
                FG.depleted_edges.append(edge)


    return RoomSelection(room_paths)

def clean_DB_room(room: Room):
    for path in room.paths:
        path.edge.remove(path)

def get_path(edge: PathEdge, traversal_type: TraversalType):

    #intentional bias in PathList order towards most-specific path type to least-specific
    match traversal_type:
        case TraversalType.ANY:
            return get_path_from_path_lists([edge.TW])
        case TraversalType.OW:
            return get_path_from_path_lists([edge.OW, edge.TW])
        case TraversalType.NOTPIZZATIME:
            return get_path_from_path_lists([edge.NPT, edge.OW, edge.TW])
        case TraversalType.PIZZATIME:
            return get_path_from_path_lists([edge.PT, edge.OW, edge.TW])

    raise ValueError(f"get_room not implemented for {traversal_type}")

def get_path_from_path_lists(path_lists: list[PathList]):

    #TODO: biased towards NDB rooms

    for pl in path_lists:

        if (len(pl.NDB) > 0):
            return pl.NDB.pop(), len(pl.NDB) == 0 #return and remove from list, return if list is emptied
        elif (len(pl.DB) > 0):
            return pl.DB.pop(), len(pl.DB) == 0

    raise RuntimeError(f"get_path_from_path_lists aclled on lists with 0 paths amongst them")

    
            