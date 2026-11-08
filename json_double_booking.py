#Author: Stack Man
#Date: 11/1/2026

#https://docs.google.com/document/d/1eIOlqorCNpQHsdbUxTMJb7THjzEMT9qhj4xVf4d3E6A/edit?tab=t.0#heading=h.qr7048wz57ow

from objects import Room, Path
from graph_collapse import pairs

#Identify and mark rooms that are capable of "double-booking"
#to prevent use of the same room multiple times in a generation

#A double-bookable room has two requirements:
#1. The room must have at least two paths.
#2. At least two of the paths don't share a start or an end transition type.
def identify_double_bookable_rooms(rooms: list[Room]):

    for room in rooms:

        #1. The room must have at least two paths.
        if (len(room.paths) < 2):
            continue

        #if (not has_three_transition_types(room.paths)):
            #continue

        #2. At least two of the paths don't share a start or an end transition type.
        has_double_bookable_paths = has_double_bookable_path_pair(room.paths)

        if (not has_double_bookable_paths):
            continue

        #Mark the room and its paths as double-bookable
        #The paths also need to know which room they are from
        room.is_double_bookable = True

        #print(f"{room} is DB")

        for path in room.paths:
            path.is_double_bookable = True
            path.room_name = room.name

def has_three_transition_types(paths: list[Path]):
    transition_types = []
    
    for path in paths:

        start_type = path.start_door.get_type_as_tuple()
        if (start_type not in transition_types):
            transition_types.append(start_type)

        if (len(transition_types) >= 3):
            break;

        exit_type = path.exit_door.get_type_as_tuple()

        if (exit_type not in transition_types):
            transition_types.append(exit_type)

        if (len(transition_types) >= 3):
            break;

    return len(transition_types) >= 3

def has_double_bookable_path_pair(paths: list[Path]):

    for path_A, path_B in pairs(paths):
        #if start or exit type is shared, skip this path combo
        if (path_A.start_door.get_type_as_tuple() == path_B.start_door.get_type_as_tuple() or
            path_A.exit_door.get_type_as_tuple() == path_B.exit_door.get_type_as_tuple()):
                continue

        #double-bookable path combination
        return True

    return False