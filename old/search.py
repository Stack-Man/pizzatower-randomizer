#Author: Stack Man
#Date: 3-26-2025

from typing import List
from objects import Room,  RoomRequirements, PathRequirements, Path, Door
from tools import exit_matches

#TODO:
""" Yields rooms that match the RoomRequirements."""
def get_rooms(rr: RoomRequirements):
    pass


#TODO:
""" Yields paths in room that match the PathRequirements"""
def get_paths(room: Room, pr: PathRequirements):
    pass


""" yields paths of a room if that:
    * has exit that is not in exits_to_trim
    * and meets the path requirements
"""
def trim_paths(room: Room, pr: PathRequirements, exits_to_trim: List[Door] = None):
    for new_path in get_paths(room, pr):

        good_exit = exits_to_trim == None or not exit_matches(new_path.exit_door, exits_to_trim)

        if good_exit:
            yield new_path


"""yields deepcopies of rooms with their paths trimmed"""
def get_rooms_and_trim_paths(rr: RoomRequirements, door_to_connect_with_start: Door, exits_to_trim: List[Door] = None):

    for room in get_rooms(rr):
        new_room = room.deepcopy()

        new_paths = []

        for new_path in trim_paths(new_room, rr.path_requirements, door_to_connect_with_start, exits_to_trim):
            new_paths.append(new_path)

        new_room.paths = new_paths
        
        yield new_room



