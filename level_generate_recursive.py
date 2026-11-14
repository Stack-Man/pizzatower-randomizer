#Author: Stack Man
#Date: 11/11/2026

#Utilize recursion to store context for each generated segment
#so that, in the event of a failed segment, we can step back
#and resume the previous segment generation from where we left off

#start (E/EB) > recursive branch/between branch (BS-BE or BE-BS)
#cap with J/JB when reached branch limit or when impossible to extend branch further

#every level of recursion creates a copy of SD/FG to avoid effecting
#the previous level of recursion in case of step back
#on cap with J/JB, return that recursion level's copy of SD/FG
#this copy will be used as the starting point for the next level generation

#1. level_generate_recursive.py: generate segments until branch limit reached or can't, then cap with J/JB
#2. level_segment_generator.py: iterators that return segments of a certain type
#3. level_bridge.py: attempts to bridge two rooms together, selecting some combination of paths in S and D to bridge with
#4. level_room_path_generator.py: iterators that return every valid path selection for a room, used by level_bridge to try different bridges
#5. 

from json_source_destination import SourceDestinationHandler

from level_objects import LevelSegment, Level, TwowaySegment, BranchSegment, BranchRoomPath
from graph_from_rooms import FlowGraphHandler

from level_segment_generator import  entrance_or_entrance_branch_segments, branch_segments, john_segment, john_branch_segment, between_branch_segments, ej_or_ejb_segment

from colors import ERROR, RESET

MIN_BRANCH_COUNT = 1

LOGGING = True

def log_sg(msg: str|Exception):
    if (LOGGING):
        print(msg)

def generate_levels_recursive_all(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    levels = []
    
    level_count = SD.entrance_count()
    i = 0

    current_SD = SD
    current_FG = FG

    try:

        while i < level_count:
            segments, new_SD, new_FG, = generate_level_recursive_start(current_SD, current_FG)
            current_SD = new_SD
            current_FG = new_FG
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
                    next_segments, new_SD, new_FG = generate_level_recursive_branch(SD, FG, last_segment=entrance_segment, branch_count=0)
                    segments = [entrance_segment]
                    segments.extend(next_segments)

                    return segments, new_SD, new_FG #continued recursive, return the terminating code's copy of SD and FG

                #if gen fails, it throws, catch and try next entrance seg
                except RuntimeError as e:
                    log_sg(e)

            else: #entrance is BranchSegment
                try:
                    #entrance was Branch so continue gen with Twoway
                    next_segments, new_SD, new_FG = generate_level_recursive_between_branch(SD, FG, last_segment=entrance_segment, branch_count=0)
                    segments = [entrance_segment]
                    segments.extend(next_segments)

                    return segments, new_SD, new_FG #continued recursive, return the terminating code's copy of SD and FG

                #if gen fails, it throws, catch and try next entrance seg
                except RuntimeError as e:
                    log_sg(e)
    except RuntimeError as e:
        log_sg(e)

    #total failure, try connecting any E or EB to any J or JB directly
    #this is the only combination not tried

    try:
        segments: list[TwowaySegment|BranchSegment] = []
        segment = ej_or_ejb_segment(SD, FG)
        segments.append(segment)
        return segments, SD, FG #terminate, return this copy of SD and FG
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
                    next_segments, new_SD, new_FG = generate_level_recursive_between_branch(SD, FG, last_segment=branch_segment, branch_count=branch_count)
                    segments = []
                    segments.append(branch_segment)
                    segments.extend(next_segments)

                    return segments, new_SD, new_FG
                except RuntimeError as e:
                    log_sg(e)

            else:
                #completed all branches, cap this branch_segment with a J
                try:
                    segment = john_segment(SD, FG, last_segment.end_room)
                    return [branch_segment, segment], SD, FG #terminate, return this copy of SD and FG
                except RuntimeError as e:
                    log_sg(e)

    #could not increase branch count, try capping with JB
    #assume that between branch would have attempted to cap a branch with J before raising an error
    try:
        segment = john_branch_segment(SD, FG, last_segment.end_room)
        return [segment], SD, FG #terminate, return this copy of SD and FG
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
                next_segments, new_SD, new_FG = generate_level_recursive_branch(SD, FG, last_segment=last_segment, branch_count=branch_count)
                segments = []
                segments.append(between_branch_segment)
                segments.extend(next_segments)

                return segments, new_SD, new_FG
            except RuntimeError as e:
                log_sg(e)

    #could not increase branch count, try capping with J
    try:
        segment = john_segment(SD, FG, last_segment.end_room)
        return [segment], SD, FG #terminate, return this copy of SD and FG
    except RuntimeError as e:
        log_sg(e)

    raise RuntimeError(f"{ERROR}Failed to generate Between Branch Segment{RESET}")


