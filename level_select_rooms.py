#Author: Stack Man
#Date: 11/11/2026

#select rooms and paths to fill the edges of the traversal

from json_objects import Room
from graph_objects import EdgeTraversal, PathEdge, TransitionEdge, PathList
from level_objects import RoomSelection, RoomPath
from graph_create import FlowGraphHandler
from enums import TraversalType
from colors import WARNING, RESET, ERROR

import logging as log

#select rooms from path list without removing them from the path list
#select rooms and track used room names to avoid reusing the same room
def select_rooms_non_empty(traversal: EdgeTraversal, traversal_type):

    #TODO traversal is not prioritizing edges from the bipartite graph the node with the fewest rooms.. impossible booking may be encountered!
    print(f"{WARNING}select_rooms does not utilize DB matching!{RESET}")

    room_paths : list[RoomPath] = []
    used_rooms : list[str] = []

    #log.debug("Start Selection for %s of type %s", traversal, traversal_type)

    e = 0

    for edge in traversal.edges:

        e += 1

        #log.debug("Edge %s of %s", e, len(traversal.edges))

        #no selection for transition edges
        if (type(edge) == TransitionEdge):
            continue

        elif (type(edge) == PathEdge):

            found = False

            for path in get_path_non_empty(edge, traversal_type):

                if (path.room_name not in used_rooms):

                    #log.debug("Edge %s use %s", e, path.room_name)

                    #track used room names since
                    #we don't clean immediately
                    used_rooms.append(path.room_name)

                    rp = RoomPath(path.room, path)
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

    return RoomSelection(room_paths)

def get_path_non_empty(edge: PathEdge, traversal_type: TraversalType):

    #intentional bias in PathList order towards most-specific path type to least-specific
    match traversal_type:
        case TraversalType.ANY:
            return get_path_from_path_lists_non_empty([edge.TW])
        case TraversalType.OW:
            return get_path_from_path_lists_non_empty([edge.OW, edge.TW])
        case TraversalType.NOTPIZZATIME:
            return get_path_from_path_lists_non_empty([edge.NPT, edge.OW, edge.TW])
        case TraversalType.PIZZATIME:
            return get_path_from_path_lists_non_empty([edge.PT, edge.OW, edge.TW])

    raise ValueError(f"get_room not implemented for {traversal_type}")
     

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


           


        
            