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
#5. level_get_traversal.py: with two room paths (source and destination), get an edge traversal that connects them
#6. level_select_rooms.py: with the traversal, choose rooms to fufill the paths selected

from json_source_destination import SourceDestinationHandler

from level_objects import LevelSegment, Level, TwowaySegment, BranchSegment, BranchRoomPath
from graph_from_rooms import FlowGraphHandler

from level_segment_generator import  entrance_or_entrance_branch_segments, branch_segments, john_segment, john_branch_segment, between_branch_segments, ej_or_ejb_segment

from colors import ERROR, RESET

MIN_BRANCH_COUNT = 1

LOGGING = True

def log_sg(msg: str|Exception):
    if (LOGGING):
        print("GEN: " + str(msg))

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

            log_sg(f"GENERATED LEVEL FROM: {segments[0].start_room.room}\n\n\n")
            
    except RuntimeError as e:
        log_sg(e)

    log_sg(f"Generated {i} levels")

    return levels, current_SD, current_FG


#TODO: should extend level by 1 branch if we cant connect to J, so we can connect to JB instead

def generate_level_recursive_start(SD: SourceDestinationHandler, FG: FlowGraphHandler):

    log_sg(f"START GENERATE RECURSIVE")

    #1. Generate the segment
    #2. recursive call generate the rest of the segments
    segments = []

    try:
        i = 0
        
        for entrance_segment in entrance_or_entrance_branch_segments(SD, FG):

            log_sg(f"SUCCESS: {entrance_segment.start_room} > {entrance_segment.end_room}")
            log_sg(f"{entrance_segment}")
            
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
                    #start with 1 branch count
                    next_segments, new_SD, new_FG = generate_level_recursive_between_branch(SD, FG, last_segment=entrance_segment, branch_count=1)
                    segments = [entrance_segment]
                    segments.extend(next_segments)

                    return segments, new_SD, new_FG #continued recursive, return the terminating code's copy of SD and FG

                #if gen fails, it throws, catch and try next entrance seg
                except RuntimeError as e:
                    log_sg(e)

            log_sg(f"DUMP: {entrance_segment.start_room} > {entrance_segment.end_room}")

        log_sg(f"Did not generate from any entrance_segment after {i} attempts")

        #total failure, try connecting any E or EB to any J or JB directly
        #this is the only combination not tried
    
    except RuntimeError as e:
        log_sg(e)

    try:
        segments: list[TwowaySegment|BranchSegment] = []
        segment = ej_or_ejb_segment(SD, FG)
        segments.append(segment)

        SD.remove_SD_in_segment(segment)

        return segments, SD, FG #terminate, return this copy of SD and FG
    except RuntimeError as e:
        log_sg(e)
    

    raise RuntimeError(f"Failed to generate any level")

#alternate between branch and between branch until target branch count is reached
#or we are forced to end with J or JB
def generate_level_recursive_branch(SD: SourceDestinationHandler, FG: FlowGraphHandler, last_segment: LevelSegment, branch_count: int):
    log_sg(f"GENERATE BRANCH SEGMENT")

    #guarantee that any recursive call has its own SD and FG
    #we make copies so that, should this recursive call step back,
    #we can immediately revert to the previous SD and FG

    #custom copy() copies only deep enough for our purposes
    SD = SD.copy() 
    FG = FG.copy() 

    #Texclude the source and destination rooms from last segment from the SD
    SD.remove_SD_in_segment(last_segment)

    segments = []

    if (type(last_segment.end_room) == BranchRoomPath):
        try:
            can_end_with_JB = len(SD.JB) > 0
            
            if (branch_count >= MIN_BRANCH_COUNT and can_end_with_JB):
                raise RuntimeError(f"Skip branch gen to end with JB")
            
            branch_count += 1

            for branch_segment in branch_segments(SD, FG, last_segment.end_room):

                log_sg(f"SUCCESS: {branch_segment.start_room} > {branch_segment.end_room}")
                log_sg(f"{branch_segment}")

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
                        segment = john_segment(SD, FG, branch_segment.end_room)
                        SD.remove_SD_in_segment(segment)
                        log_sg(f"John Generated: {segment.start_room} > {segment.end_room}")
                        return [branch_segment, segment], SD, FG #terminate, return this copy of SD and FG
                    except RuntimeError as e:
                        log_sg("J cap from branch_segment: " + str(e))

                log_sg(f"DUMP: {branch_segment.start_room} > {branch_segment.end_room}")

            raise RuntimeError(f"Failed to gen non JB branch from {last_segment.end_room.room}")

        except RuntimeError as e:
            log_sg(e)
            
            #could not increase branch count, try capping with JB
            #assume that between branch would have attempted to cap a branch with J before raising an error
            try:
                log_sg(f"Try generate JB from {last_segment.end_room.room}")
                segment = john_branch_segment(SD, FG, last_segment.end_room)
                SD.remove_SD_in_segment(segment)
                log_sg(f"John Generated: {segment.start_room} > {segment.end_room}")
                return [segment], SD, FG #terminate, return this copy of SD and FG
            except RuntimeError as e:
                log_sg(e)

    else:
        raise ValueError(f"last_segment was not BranchRoomPath")

    raise RuntimeError(f"{ERROR}Failed to generate Branch Segment{RESET}")

def generate_level_recursive_between_branch(SD: SourceDestinationHandler, FG: FlowGraphHandler, last_segment: LevelSegment, branch_count: int):
    log_sg(f"GENERATE TWOWAY SEGMENT")
    
    SD = SD.copy() 
    FG = FG.copy()

    SD.remove_SD_in_segment(last_segment)

    segments = []

    #typecast end room to BranchRoomPath
    #check branch count again in case we want to immediately add a john
    #but go ahead anyways if we cant end with J

    can_end_with_J = len(SD.J) > 0

    if (type(last_segment.end_room) == BranchRoomPath and (branch_count < MIN_BRANCH_COUNT or not can_end_with_J)):

        log_sg(f"continuing with TW seg gen")

        for between_branch_segment in between_branch_segments(SD, FG, last_segment.end_room):

            log_sg(f"SUCCESS: {between_branch_segment.start_room} > {between_branch_segment.end_room}")
            log_sg(f"{between_branch_segment}")

            try: 
                next_segments, new_SD, new_FG = generate_level_recursive_branch(SD, FG, last_segment=between_branch_segment, branch_count=branch_count)
                segments = []
                segments.append(between_branch_segment)
                segments.extend(next_segments)

                return segments, new_SD, new_FG
            except RuntimeError as e:
                log_sg(e)

            log_sg(f"DUMP: {between_branch_segment.start_room} > {between_branch_segment.end_room}")
    else:
        log_sg(f"last seg end is branch?: {type(last_segment.end_room) == BranchRoomPath} branch count < MIN? {branch_count} < {MIN_BRANCH_COUNT} can end with J? {can_end_with_J}")


    #could not increase branch count, try capping with J
    try:
        log_sg(f"Try J segment from {last_segment.end_room}")
        segment = john_segment(SD, FG, last_segment.end_room)
        SD.remove_SD_in_segment(segment)
        log_sg(f"John Generated: {segment.start_room} > {segment.end_room}")
        return [segment], SD, FG #terminate, return this copy of SD and FG
    except RuntimeError as e:
        log_sg(e)

    raise RuntimeError(f"{ERROR}Failed to generate Between Branch Segment{RESET}")


