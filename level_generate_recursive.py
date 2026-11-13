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
from level_objects import LevelSegment, Level
from graph_from_rooms import FlowGraphHandler

MIN_BRANCH_COUNT = 1
LOG_FAILED_SEGMENT_GEN = True

def log_sg(msg: str|RuntimeError):
    if (LOG_FAILED_SEGMENT_GEN):
        print(msg, flush = True)


#TODO: we must pass the deepest-copy SD and FG through the return 
# so that the can exist as the starting point for the next level generation

def generate_levels_recursive_all(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    levels = []
    
    level_count = SD.entrance_count()
    i = 0

    try:

        while i < level_count:
            segments = generate_level_recursive_start(SD, FG)
            levels.append(Level(segments=segments))
            i += 1
            
    except RuntimeError as e:
        log_sg(e)

    log_sg(f"Generated {i} levels")
    return levels

def generate_level_recursive_start(SD: SourceDestinationHandler, FG: FlowGraphHandler):

    #1. Generate the segment
    #2. recursive call generate the rest of the segments
    segments = []

    try:
        for entrance_segment in entrance_or_entrance_branch_segments(SD, FG):
            if (type(entrance_segment) == TwowaySegment):

                #if rest of segments generate from this seg, extend and return
                try:
                    #entrance was Twoway, so continue gen with Branch
                    next_segments = generate_level_recursive_branch(SD, FG, last_segment=entrance_segment, branch_count=0)
                    segments = [entrance_segment]
                    segments.extend(next_segments)

                    return segments

                #if gen fails, it throws, catch and try next entrance seg
                except RuntimeError as e:
                    log_sg(e)

            else: #entrance is BranchSegment
                try:
                    #entrance was Branch so continue gen with Twoway
                    next_segments = generate_level_recursive_between_branch(SD, FG, last_segment=entrance_segment, branch_count=0)
                    segments = [entrance_segment]
                    segments.extend(next_segments)

                    return segments

                #if gen fails, it throws, catch and try next entrance seg
                except RuntimeError as e:
                    log_sg(e)
    except RuntimeError as e:
        log_sg(e)

    #total failure, try connecting any E or EB to any J or JB directly
    #this is the only combination not tried

    try:
        segments: list[TwowaySegment|BranchSegment] = []
        segments.append(ej_or_ejb_segment(SD, FG))
        return segments
    except RuntimeError as e:
        log_sg(e)

    raise RuntimeError(f"Failed to generate any level")

#alternate between branch and between branch until target branch count is reached
#or we are forced to end with J or JB
def generate_level_recursive_branch(SD: SourceDestinationHandler, FG: FlowGraphHandler, last_segment: LevelSegment, branch_count: int):

    #guarantee that any recursive call has its own SD and FG
    #we make copies so that, should this recursive call step back,
    #we can immediately revert to the previous SD and FG

    #custom copy() copies only deep enough for our purposes
    SD = SD.copy() 
    FG = FG.copy() 

    segments = []

    if (type(last_segment.end_room) == BranchRoomPath):

        branch_count += 1

        for branch_segment in branch_segments(SD, FG, last_segment.end_room):

            if (branch_count < MIN_BRANCH_COUNT): #continue adding branch segments

                try:
                    next_segments = generate_level_recursive_between_branch(SD, FG, last_segment=branch_segment, branch_count=branch_count)
                    segments = []
                    segments.append(branch_segment)
                    segments.extend(next_segments)

                    return segments
                except RuntimeError as e:
                    log_sg(e)

            else:
                #completed all branches, cap this branch_segment with a J
                try:
                    return [branch_segment, john_segment(SD, FG, last_segment.end_room)]
                except RuntimeError as e:
                    log_sg(e)

    #could not increase branch count, try capping with JB
    #assume that between branch would have attempted to cap a branch with J before raising an error
    try:
        return [john_branch_segment(SD, FG, last_segment.end_room)]
    except RuntimeError as e:
        log_sg(e)

    raise RuntimeError(f"{ERROR}Failed to generate Branch Segment{RESET}")

def generate_level_recursive_between_branch(SD: SourceDestinationHandler, FG: FlowGraphHandler, last_segment: LevelSegment, branch_count: int):
    SD = SD.copy() 
    FG = FG.copy()

    segments = []

    #typecast end room to BranchRoomPath
    #check branch count again in case we want to immediately add a john
    if (type(last_segment.end_room) == BranchRoomPath and branch_count < MIN_BRANCH_COUNT):

        for between_branch_segment in between_branch_segments(SD, FG, last_segment.end_room):

            try: 
                next_segments = generate_level_recursive_branch(SD, FG, last_segment=last_segment, branch_count=branch_count)
                segments = []
                segments.append(between_branch_segment)
                segments.extend(next_segments)

                return segments
            except RuntimeError as e:
                log_sg(e)

    #could not increase branch count, try capping with J
    try:
        return [john_segment(SD, FG, last_segment.end_room)]
    except RuntimeError as e:
        log_sg(e)

    raise RuntimeError(f"{ERROR}Failed to generate Between Branch Segment{RESET}")


def entrance_or_entrance_branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    #Pick either E or EB
    for E_or_EB in SD.entrances():
        E_or_EB.print_stats()
        #if E, create a TwowaySegment with E and some BS
        if (E_or_EB.branch_type == BranchType.NONE):
            log_sg(f"entrance_or_entrance_branch_segments: {E_or_EB} was E")
            for BS_or_BA in SD.branch_starts(): 
                for seg in bridge_twoway_room_room(E_or_EB, BS_or_BA, FG):     
                    yield seg
        #if EB, create a Branch Segment with EB and some BE
        else:
            log_sg(f"entrance_or_entrance_branch_segments: {E_or_EB} was EB")
            for BE_or_BA in SD.branch_ends():
                for seg in bridge_branch_room_room(E_or_EB, BE_or_BA, FG):
                    yield seg

    raise RuntimeError(f"Failed to generate any E or EB segment")

def branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler, BS: BranchRoomPath):
    #create a BranchSegment with BS and some BE or JB
    for BA_or_BE in SD.branch_ends():
        for seg in bridge_branch_rp_room(BS, BA_or_BE, FG):
            yield seg

    raise RuntimeError(f"Failed to generate any branch segment from {BS.room}")

def john_branch_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler, BS_or_EB: BaseRoomPath):
    #create TwowaySegment with BE or E and some J
    for JB in SD.john_branches():
        for seg in bridge_twoway_rp_room(BS_or_EB, JB, FG):
            return seg #return the first successful bridge

    raise RuntimeError(f"Failed to generate John Branch segment from {BS_or_EB.room}")

def john_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler, BE_or_E: BaseRoomPath):
    #create TwowaySegment with BE or E and some J
    for J in SD.just_johns():
        for seg in bridge_twoway_rp_room(BE_or_E, J, FG):
            return seg #return the first successful bridge

    raise RuntimeError(f"Failed to generate any John segment from {BE_or_E.room}")

def between_branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler, BE: BaseRoomPath):
    #create TwowaySegment with Be and some BS or BA

    for BA_or_BS in SD.branch_starts():
        for seg in bridge_twoway_rp_room(BE, BA_or_BS, FG):
            yield seg

    raise RuntimeError(f"Failed to generate any between branch segment from {BE.room}")

def ej_or_ejb_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    #Create TwowaySegemnt between E and J or BranchSegment between EB and JB

    #Pick either E or EB
    try:
        for E_or_EB in SD.entrances():
            #if E, create a TwowaySegment with E and some J

            log_sg(f"ej_or_ejb_segment with {E_or_EB} of branch type {E_or_EB.branch_type}")

            if (E_or_EB.branch_type == BranchType.NONE):
                for J in SD.just_johns(): 
                    for seg in bridge_twoway_room_room(E_or_EB, J, FG):     
                        return seg #return first valid seg
                raise RuntimeError(f"No J to match E {E_or_EB}")
            #if EB, create a Branch Segment with EB and some JB
            else:
                for JB in SD.john_branches():
                    for seg in bridge_branch_room_room(E_or_EB, JB, FG):
                        return seg
                raise RuntimeError(f"No JB to match EB {E_or_EB}")
    except RuntimeError as e:
        log_sg(e)
    
    raise RuntimeError(f"Failed to generate any EJ or EJB segment")