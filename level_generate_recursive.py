#Author: Stack Man
#Date: 11/11/2026

#Utilize recursion to store context for each generated segment
#so that, in the event of a failed segment, we can step back
#and resume the previous segment generation from where we left off

from json_source_destination import SourceDestinationHandler
from level_bridge import *
from enums import BranchType
from level_objects import LevelSegment

#TODO: have to make a copy of SD every recursion level to prevent later modification from affecting earlier iteration on step back
#for example, a consumed SD is removed from E then readded
#it gets added to the end of E, even if it was originally from the middle

#copy the SD when making the recursive call

MIN_BRANCH_COUNT = 1

def generate_level_recursive_start(SD: SourceDestinationHandler, FG):

    #1. Generate the segment
    #2. recursive call generate the next segment

    segments = []

    for entrance_segment in entrance_or_entrance_branch_segments(SD, FG):

        if (type(entrance_segment.end_room.room.branch_type) == BranchType.START): #TODO: have to account for forced start or forced end

            #if rest of segments generate from this seg, extend and return
            try:
                #copy the SD before recursive call so that we can maintain a unique copy of SD
                #for this recursion depth, in case of step back
                next_segments = generate_level_recursive_branch(SD.copy(), FG, last_segment=entrance_segment, branch_count=0)
                segments = [entrance_segment]
                segments.extend(next_segments)

            #if gen fails, it throws, catch and try next entrance seg
            except Exception as e:
                print(e)

        else:
            continue #TODO: connect to J immediately if BranchType.END

    return segments

def generate_level_recursive_branch(SD: SourceDestinationHandler, FG, last_segment: LevelSegment, branch_count: int):

    segments = []

    force_john = branch_count >= MIN_BRANCH_COUNT and len(SD.J) <= 0

    if (type(last_segment.end_room) == BranchRoomPath):

        branch_count += 1

        for branch_segment in branch_segments(SD, FG, last_segment.end_room, force_john):

            if (branch_count < MIN_BRANCH_COUNT): #continue adding branch segments

                try:
                    next_segments = generate_level_recursive_branch(SD.copy(), FG, last_segment=branch_segment, branch_count=branch_count)
                    segments = [branch_segment]
                    segments.extend(next_segments)

                    return segments
                except Exception as e:
                    print(e)

            else:
                continue #TODO: generate J segment

    raise RuntimeError(f"{ERROR}Failed to generate Branch Segment{RESET}")

def entrance_or_entrance_branch_segments(SD: SourceDestinationHandler, FG):
    #Pick either E or EB
    for E_or_EB in SD.entrances():
        #if E, create a TwowaySegment with E and some BS
        if (type(E_or_EB.branch_type) == BranchType.NONE):
            for BS_or_BA in SD.branch_starts():
                #TODO: check SD type combo not in memory
                for seg in bridge_twoway_room_room(E_or_EB, BS_or_BA, FG):
                    yield seg
                #TODO: failed, store SD type combo in memory
        #if EB, create a Branch Segment with EB and some BE
        else:
            for BE_or_BA in SD.branch_ends():
                #TODO: check SD type combo not in memory
                for seg in bridge_branch_room_room(E_or_EB, BE_or_BA, FG):
                    yield seg
                #TODO: failed, store SD type combo in memory

def branch_segments(SD: SourceDestinationHandler, FG, BS: BranchRoomPath, force_john_end: bool):
    #create a BranchSegment with BS and some BE or JB
    for BA_BE_or_JB in SD.branch_ends_or_john_branch_ends(force_john_end):
        #TODO: check SD type combo not in memory
        for seg in bridge_branch_rp_room(BS, BA_BE_or_JB, FG):
            yield seg
        #TODO: failed, store SD type combo in memory

def john_segments(SD: SourceDestinationHandler, FG, BE_or_E: BaseRoomPath):
    #create TwowaySegment with BE or E and some J
    for J in SD.johns():
        #TODO: check SD type combo not in memory
        for seg in bridge_twoway_rp_room(BE_or_E, J, FG):
            yield seg
        #TODO: failed, store SD type combo in memory