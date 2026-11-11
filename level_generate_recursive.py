#Author: Stack Man
#Date: 11/11/2026

#Utilize recursion to store context for each generated segment
#so that, in the event of a failed segment, we can step back
#and resume the previous segment generation from where we left off

#start (E/EB) > recursive branch/between branch (BS-BE or BE-BS)
#cap with J/JB when reached branch limit or when impossible to extend branch further

from json_source_destination import SourceDestinationHandler
from level_bridge import *
from enums import BranchType
from level_objects import LevelSegment


#TODO: Memory Set is flawed, on step back, we release some paths so failed SD pairs may no longer be failed...

MIN_BRANCH_COUNT = 1

from level_sd_memory_set import *

LOG_FAILED_SEGMENT_GEN = True

def log_sg(msg: str|Exception):
    if (LOG_FAILED_SEGMENT_GEN):
        print(msg)

def generate_level_recursive_start(SD: SourceDestinationHandler, FG):

    #1. Generate the segment
    #2. recursive call generate the rest of the segments
    segments = []
    memory_set = MemorySet()

    for entrance_segment in entrance_or_entrance_branch_segments(SD, FG, MS = memory_set):

        if (type(entrance_segment.end_room.room.branch_type) == BranchType.START): #TODO: have to account for forced start or forced end

            #if rest of segments generate from this seg, extend and return
            try:
                #BranchType.START, so generate branch first
                next_segments = generate_level_recursive_branch(SD, FG, MS = memory_set, last_segment=entrance_segment, branch_count=0)
                segments = [entrance_segment]
                segments.extend(next_segments)

                return segments

            #if gen fails, it throws, catch and try next entrance seg
            except Exception as e:
                log_sg(e)

        else: #BranchType.END, so generate between branches first
            try:
                next_segments = generate_level_recursive_between_branch(SD, FG, MS = memory_set, last_segment=entrance_segment, branch_count=0)
                segments = [entrance_segment]
                segments.extend(next_segments)

                return segments

            #if gen fails, it throws, catch and try next entrance seg
            except Exception as e:
                log_sg(e)

    #total failure, try connecting any E or EB to any J or JB directly
    #this is the only combination not tried

    try:
        return ej_or_ejb_segment(SD, FG, MS = memory_set)
    except Exception as e:
        log_sg(e)

    raise RuntimeError(f"Failed to generate any level")

#alternate between branch and between branch until target branch count is reached
#or we are forced to end with J or JB
def generate_level_recursive_branch(SD: SourceDestinationHandler, FG, MS: MemorySet, last_segment: LevelSegment, branch_count: int):
    SD = SD.copy() #guarantee that any recursive call has its own SD

    segments = []

    if (type(last_segment.end_room) == BranchRoomPath):

        branch_count += 1

        for branch_segment in branch_segments(SD, FG, MS, last_segment.end_room):

            if (branch_count < MIN_BRANCH_COUNT): #continue adding branch segments

                try:
                    next_segments = generate_level_recursive_between_branch(SD, FG, MS, last_segment=branch_segment, branch_count=branch_count)
                    segments = []
                    segments.append(branch_segment)
                    segments.extend(next_segments)

                    return segments
                except Exception as e:
                    log_sg(e)

            else:
                #completed all branches, cap this branch_segment with a J
                try:
                    return [branch_segment, john_segment(SD, FG, MS, last_segment.end_room)]
                except Exception as e:
                    log_sg(e)

    #could not increase branch count, try capping with JB
    #assume that between branch would have attempted to cap a branch with J before raising an error
    try:
        return [john_branch_segment(SD, FG, MS, last_segment.end_room)]
    except Exception as e:
        log_sg(e)

    raise RuntimeError(f"{ERROR}Failed to generate Branch Segment{RESET}")

def generate_level_recursive_between_branch(SD: SourceDestinationHandler, FG, MS: MemorySet, last_segment: LevelSegment, branch_count: int):
    SD = SD.copy()

    segments = []

    #typecast end room to BranchRoomPath
    #check branch count again in case we want to immediately add a john
    if (type(last_segment.end_room) == BranchRoomPath and branch_count < MIN_BRANCH_COUNT):

        for between_branch_segment in between_branch_segments(SD, FG, MS, last_segment.end_room):

            try: 
                next_segments = generate_level_recursive_branch(SD, FG, MS, last_segment=last_segment, branch_count=branch_count)
                segments = []
                segments.append(between_branch_segment)
                segments.extend(next_segments)

                return segments
            except Exception as e:
                log_sg(e)

    #could not increase branch count, try capping with J
    try:
        return [john_segment(SD, FG, MS, last_segment.end_room)]
    except Exception as e:
        log_sg(e)

    raise RuntimeError(f"{ERROR}Failed to generate Between Branch Segment{RESET}")


def entrance_or_entrance_branch_segments(SD: SourceDestinationHandler, FG, MS):
    #Pick either E or EB
    for E_or_EB in SD.entrances():
        #if E, create a TwowaySegment with E and some BS
        if (type(E_or_EB.branch_type) == BranchType.NONE):
            for BS_or_BA in SD.branch_starts(): 
                for seg in bridge_twoway_room_room(E_or_EB, BS_or_BA, FG, MS):     
                    yield seg
        #if EB, create a Branch Segment with EB and some BE
        else:
            for BE_or_BA in SD.branch_ends():
                for seg in bridge_branch_room_room(E_or_EB, BE_or_BA, FG, MS):
                    yield seg

    raise RuntimeError(f"Failed to generate any E or EB segment")

def branch_segments(SD: SourceDestinationHandler, FG, MS: MemorySet, BS: BranchRoomPath):
    #create a BranchSegment with BS and some BE or JB
    for BA_or_BE in SD.branch_ends():
        for seg in bridge_branch_rp_room(BS, BA_or_BE, FG, MS):
            yield seg

    raise RuntimeError(f"Failed to generate any branch segment from {BS.room}")

def john_branch_segment(SD: SourceDestinationHandler, FG, MS: MemorySet, BS_or_EB: BaseRoomPath):
    #create TwowaySegment with BE or E and some J
    for JB in SD.john_branches():
        for seg in bridge_twoway_rp_room(BS_or_EB, JB, FG, MS):
            return seg #return the first successful bridge

    raise RuntimeError(f"Failed to generate John Branch segment from {BS_or_EB.room}")

def john_segment(SD: SourceDestinationHandler, FG, MS: MemorySet, BE_or_E: BaseRoomPath):
    #create TwowaySegment with BE or E and some J
    for J in SD.just_johns():
        for seg in bridge_twoway_rp_room(BE_or_E, J, FG, MS):
            return seg #return the first successful bridge

    raise RuntimeError(f"Failed to generate any John segment from {BE_or_E.room}")

def between_branch_segments(SD: SourceDestinationHandler, FG, MS: MemorySet, BE: BaseRoomPath):
    #create TwowaySegment with Be and some BS or BA

    for BA_or_BS in SD.branch_starts():
        for seg in bridge_twoway_rp_room(BE, BA_or_BS, FG, MS):
            yield seg

    raise RuntimeError(f"Failed to generate any between branch segment from {BE.room}")

def ej_or_ejb_segment(SD: SourceDestinationHandler, FG, MS: MemorySet):
    #Create TwowaySegemnt between E and J or BranchSegment between EB and JB

    #Pick either E or EB
    for E_or_EB in SD.entrances():
        #if E, create a TwowaySegment with E and some J
        if (type(E_or_EB.branch_type) == BranchType.NONE):
            for J in SD.just_johns(): 
                for seg in bridge_twoway_room_room(E_or_EB, J, FG, MS):     
                    return seg #return first valid seg
        #if EB, create a Branch Segment with EB and some JB
        else:
            for JB in SD.john_branches():
                for seg in bridge_branch_room_room(E_or_EB, JB, FG, MS):
                    return seg
    
    raise RuntimeError(f"Failed to generate any EJ or EJB segment")