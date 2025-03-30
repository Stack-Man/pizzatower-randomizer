#Author: Stack Man
#Date: 3-26-2025

from typing import List
from objects import Room,  RoomRequirements, PathRequirements, Path, Door

#TODO:
""" Yields a room that matches the RoomRequirements.
    If trim_paths is True, will yield the room without the paths that don't match RoomRequirements.path_requirements
    if exits_to_trim is defined, we will also trim paths with exits that match
"""
def get_rooms(requirements: RoomRequirements, trim_paths: bool = False, exits_to_trim: List[Door] = None) -> Room:

    #look through all rooms
    #yield room IF paths.size > 0
    
    #TODO: yield a deepcopy of the room if we're trimming paths

    pass

def get_paths(room: Room, requirements: PathRequirements) -> Path:
    pass
