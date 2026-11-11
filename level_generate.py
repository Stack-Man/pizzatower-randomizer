#Author: Stack Man
#Date: 11/9/2026

#Generate an entire level
#Select SD combos and attempt to bridge them

from objects import Room
from level_objects import *
from json_source_destination import SourceDestinationHandler
from enums import BranchType
from colors import WARNING, RESET, ERROR
from level_bridge import *


def generate_levels_all(SD: SourceDestinationHandler, FG):

    levels = []

    level_count = SD.entrance_count()
    i = 0

    while i < level_count:

        level = generate_level(SD, FG)
        levels.append(level)
        i += 1

    return levels

def generate_level(SD: SourceDestinationHandler, FG):

    #TODO: implement step back for total failure, with SD memory to avoid re-treading each step back
    #TODO: each failed start_rp, end_rp combo shuold be remembered, by path exit and start type, to avoid re-treads

    #Pick either E or EB
    #if E, create a TwowaySegment with E and some BS
    #if EB, create a Branch Segment with EB and some BE

    segments = []

    #TODO: if no J and EB, force connect EB to JB 
    E_segment = generate_entrance_or_entrance_branch_segment(SD, FG)
    segments.append(E_segment)

    #if E, pick BE or JB
    #create a BranchSegment with BS and some BE or JB
    john_count = len(SD.J)

    if (type(E_segment) == TwowaySegment):
        force_john = john_count <= 0 #force JB end if no J exists

        #TODO: catch if gen fails
        if (type(E_segment.end_room) == BranchRoomPath):
            B_segment = generate_branch_segment(SD, FG, E_segment.end_room, force_john)
            segments.append(B_segment)
        else:
            print(f"{ERROR}ERROR: E_segment was twoway but end_room was not BranchRoomPath{RESET}")

    #if BE, pick J
    #Create a BranchSegment with BE and J
    last_segment = segments[len(segments) - 1]

    if (not last_segment.is_john):

        J_segment = generate_john_segment(SD, FG, last_segment.end_room)
        segments.append(J_segment)

    return Level(segments)

def generate_entrance_or_entrance_branch_segment(SD: SourceDestinationHandler, FG):

    #Pick either E or EB
    
    #if EB, create a Branch Segment with EB and some BE
    E_or_EB_room = SD.get_entrance()

    #if E, create a TwowaySegment with E and some BS
    if (type(E_or_EB_room.branch_type) == BranchType.NONE):
        BS_or_BA_room = SD.get_branch_start()
        return bridge_twoway_room_room(E_or_EB_room, BS_or_BA_room, FG)
    else:
        BE_or_BA_room = SD.get_branch_end()
        return bridge_branch_room_room(E_or_EB_room, BE_or_BA_room, FG)


def generate_branch_segment(SD: SourceDestinationHandler, FG, start_room: BranchRoomPath, force_john_end: bool):
    #create a BranchSegment with BS and some BE or JB

    BA_BE_or_JB_room = SD.get_john_branch_or_branch_end(force_john_end)
    return bridge_branch_rp_room(start_room, BA_BE_or_JB_room, FG)

def generate_john_segment(SD: SourceDestinationHandler, FG, start_room: BaseRoomPath):

    J_room = SD.get_john_no_branch()

    return bridge_twoway_rp_room(start_room, J_room, FG)