#Author: Stack Man
#Date: 11/11/2026

#select rooms and paths to fill the edges of the traversal

from json_objects import Path
from graph_objects import EdgeTraversal, PathEdge, TransitionEdge, PathList
from level_objects import RoomSelection, RoomPath
from enums import TraversalType, PathTime
from colors import WARNING, RESET, ERROR

import logging as log

#select rooms from path list without removing them from the path list
#select rooms and track used room names to avoid reusing the same room
def select_rooms_non_empty(traversal: EdgeTraversal, traversal_type: TraversalType):
    #store matches by edge so that they
    #can be reconsructed afterwards even
    #if we do it out of order due to DB matching
    matching : dict[PathEdge, RoomPath] = {} 
    matching_DB = traversal.get_matching(traversal_type)
    has_DB_matching = len(matching_DB.keys()) != 0

    if (has_DB_matching):
        matching = select_rooms_from_matching(traversal_type, matching_DB)

    room_paths : list[RoomPath] = []
    used_rooms : list[str] = []

    #if (len(traversal) == 3 and traversal.edges[0] == traversal.edges[2]):
        #log.debug("============SELECTING FOR REPEAT TRAVERSAL")

    for edge in traversal.edges:

        #no selection for transition edges
        if (type(edge) == TransitionEdge):
            #log.debug("Skip Transition Edge")
            continue

        elif (type(edge) == PathEdge):
            #log.debug("Do Path Edge")

            #skip DB edges that are already in the matchign
            if (has_DB_matching):
                if edge in matching:
                    continue

            found = False

            for path in get_path_from_path_lists_non_empty(edge.get_path_lists(traversal_type)):

                if (path.room_name not in used_rooms):
                    #track used room names since
                    #we don't clean immediately
                    used_rooms.append(path.room_name)

                    rp = RoomPath(path.room, path)

                    #if matching, store edge, RP in matching
                    if (has_DB_matching):
                        matching[edge] = rp
                    #use list directly if no DB matching
                    else: 
                        room_paths.append(rp)

                    #exit to next edge
                    found = True
                    break

            #failed to choose path for edge
            #should never happen if impossible bookings
            #are properly avoided (currently, NOT)
            if (not found):
                raise LookupError("No non-used path for edge but selection should be possible")
        
        else:

            raise ValueError(f"Edge not of type Transition or Path but {str(type(edge))}")

    #reconstruct room paths list from matching dict
    if (has_DB_matching):
        for edge in traversal:
            if (type(edge) == PathEdge):
                room_paths.append(matching[edge])

    return RoomSelection(room_paths)

def select_rooms_from_matching( traversal_type: TraversalType, matching_DB: dict[PathEdge, str]):

    matching : dict[PathEdge, RoomPath] = {} 

    for edge in matching_DB.keys():

        #from edge, get the room name and path that matches the edeg and traversal type
        path_lists = edge.get_path_lists(traversal_type)
        target_room_name = matching_DB[edge]

        found = False

        for PL in path_lists:
            for P in PL:

                #on target path found, braek out of loop
                if P.room_name == target_room_name and matches_traversal_type(P, traversal_type):
                    matching[edge] = RoomPath(P.room, P)
                    found = True
                    break

            #path was found, stop
            if (found):
                break

    return matching

def matches_traversal_type(path: Path, traversal_type: TraversalType):

    match traversal_type:
        case TraversalType.ANY:
            return not path.oneway and path.get_path_time() == PathTime.BOTH
        case TraversalType.NOTPIZZATIME:
            return path.get_path_time() in [PathTime.NOTPIZZATIME, PathTime.BOTH]
        case TraversalType.PIZZATIME:
            return path.get_path_time() in [PathTime.PIZZATIME, PathTime.BOTH]
        case TraversalType.OW:
            return path.get_path_time == path.get_path_time() == PathTime.BOTH
            
                    
        
    
def get_path_from_path_lists_non_empty(path_lists: list[PathList]):

    #TODO: biased towards NDB rooms

    i = 0

    for pl in path_lists:

        for p in pl.NDB:
            i += 1
            yield p

        for p in pl.DB:
            i += 1
            yield p

    if (i == 0):
        raise RuntimeError(f"get_path_from_path_lists called on lists with 0 paths amongst them")


           


        
            