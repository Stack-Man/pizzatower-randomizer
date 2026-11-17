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

from perf_counter import PerfType, start_perf, end_perf, print_perf_type
import logging as log
from colors import ERROR, RESET, CONTINUE, FAIL, CAUTION

#TODO: min branch count should be a configurable parameter
#STARTING min branch count, we increase this if we fail to cap with the current amount
MIN_BRANCH_COUNT = 1
MAX_BRANCH_COUNT = 2

#TODO: branching tries many branch segments even if the continuation fails many times
#possibly trying redundant paths after? could we reduce? but have to account for path replenishing...
#seems to try the segment, then just gives up without continuing to a between branch...

def generate_levels_recursive_all(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    levels = []
    
    level_count = SD.entrance_count()
    i = 0

    current_SD = SD
    current_FG = FG

    try:

        while i < level_count:
            start_perf(PerfType.GEN)

            segments, new_SD, new_FG, = generate_level_recursive_start(current_SD, current_FG)
            current_SD = new_SD
            current_FG = new_FG

            level = Level(segments=segments)
            levels.append(level)
            i += 1

            end_perf(PerfType.GEN)
            print_perf_type(PerfType.GEN)
            log.debug("%i: %s", i, level)
            

    except RuntimeError as e:
        pass


    log.debug("Generated %i levels of %i", i, level_count)

    return levels, current_SD, current_FG

def generate_level_recursive_start(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    log.debug("START")

    if (len(SD.J) <= 0 and len(SD.JB) <= 0):
        log.debug("%sOut of J and JB%s", ERROR, RESET)
        raise RuntimeError(f"No J or JB to build to")
    else:
        log.debug("%sJs left: %i, JBs left: %i%s", CAUTION, len(SD.J), len(SD.JB), RESET)
        log.debug("%sEs left: %i, EBs left: %i%s", CAUTION, len(SD.E), len(SD.EB), RESET)
        log.debug("%sBSs left: %i, BEs left: %i, BAs left:%i%s", CAUTION, len(SD.BS), len(SD.BE), len(SD.BA), RESET)
    
    try:
        i = 0
        
        for entrance_segment in entrance_or_entrance_branch_segments(SD, FG):

            log.debug("%sTRY entrance_segment: %s to %s%s", CONTINUE, entrance_segment.start_room, entrance_segment.end_room, RESET)

            if (type(entrance_segment) == TwowaySegment):

                #if rest of segments generate from this seg, extend and return
                try:
                    #entrance was Twoway, so continue gen with Branch
                    next_segments, new_SD, new_FG = generate_level_recursive_branch(SD, FG, last_segment=entrance_segment, branch_count=0, min_branch_count=MIN_BRANCH_COUNT)
                    segments = [entrance_segment]
                    segments.extend(next_segments)

                    return segments, new_SD, new_FG #continued recursive, return the terminating code's copy of SD and FG

                #if gen fails, it throws, catch and try next entrance seg
                except RuntimeError as e:
                    pass

            else: #entrance is BranchSegment
                try:
                    #entrance was Branch so continue gen with Twoway
                    #start with 1 branch count
                    next_segments, new_SD, new_FG = generate_level_recursive_between_branch(SD, FG, last_segment=entrance_segment, branch_count=1, min_branch_count=MIN_BRANCH_COUNT)
                    segments = [entrance_segment]
                    segments.extend(next_segments)

                    return segments, new_SD, new_FG #continued recursive, return the terminating code's copy of SD and FG

                #if gen fails, it throws, catch and try next entrance seg
                except RuntimeError as e:
                    pass

            log.debug("%sDUMP entrance_segment: %s to %s%s", FAIL, entrance_segment.start_room, entrance_segment.end_room, RESET)
            
        #total failure, try connecting any E or EB to any J or JB directly
        #this is the only combination not tried
    
    except RuntimeError as e:
        pass

    try:
        log.debug("TRY immediate E to J")
        
        segments: list[TwowaySegment|BranchSegment] = []
        segment = ej_or_ejb_segment(SD, FG)
        segments.append(segment)

        SD.remove_SD_in_segment(segment)

        log.debug("%sE to J: %s to %s%s", CONTINUE, segment.start_room, segment.end_room, RESET)
        return segments, SD, FG #terminate, return this copy of SD and FG
    except RuntimeError as e:
        pass
    

    raise RuntimeError(f"Failed to generate any level")

#alternate between branch and between branch until target branch count is reached
#or we are forced to end with J or JB
def generate_level_recursive_branch(SD: SourceDestinationHandler, FG: FlowGraphHandler, last_segment: LevelSegment, branch_count: int, min_branch_count: int):
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
            
            if (branch_count >= min_branch_count and can_end_with_JB):
                log.debug("%sSKIP branch gen, go directly to JB%s", CAUTION, RESET)
                raise RuntimeError(f"Skip branch gen to end with JB")
            
            branch_count += 1

            for branch_segment in branch_segments(SD, FG, last_segment.end_room):

                log.debug("%sTRY branch_segment: %s to %s%s", CONTINUE, branch_segment.start_room, branch_segment.end_room, RESET)

                tried_J = False
                
                #At desired branch count, try  cap with J
                if (branch_count >= min_branch_count):
                    tried_J = True

                    try:
                        return try_cap_with_J_branch(SD, FG, branch_segment=branch_segment)
                    except RuntimeError as e:
                        log.debug("%sNo J from BE (MIN BRANCH)%s", FAIL, RESET)

                        #failed J with curent branch count, continue branch gen
                        min_branch_count += 1

                        if (min_branch_count > MAX_BRANCH_COUNT):
                            min_branch_count = MAX_BRANCH_COUNT

                        pass



                #check in case target branch count was not actually increased
                if (branch_count < min_branch_count):
                    #Failed to cap with J or not at desired branch count
                    try:
                        next_segments, new_SD, new_FG = generate_level_recursive_between_branch(SD, FG, last_segment=branch_segment, branch_count=branch_count, min_branch_count=min_branch_count)
                        segments = []
                        segments.append(branch_segment)
                        segments.extend(next_segments)

                        return segments, new_SD, new_FG
                    except RuntimeError as e:

                        if (not tried_J):
                            try:
                                return try_cap_with_J_branch(SD, FG, branch_segment=branch_segment)
                            except RuntimeError as e:
                                log.debug("%sNo J from BE (MAX BRANCH)%s", FAIL, RESET)
                                pass
                else:
                    log.debug("max branch but failed J")
                    

                log.debug("%sDUMP branch_segment: %s to %s%s", FAIL, branch_segment.start_room, branch_segment.end_room, RESET)

            raise RuntimeError(f"Failed to gen non JB branch from {last_segment.end_room.room}")

        except RuntimeError as e:

            #could not increase branch count, try capping with JB
            #assume that between branch would have attempted to cap a branch with J before raising an error
            try:
                log.debug("Try BS to JB")

                
                segment = john_branch_segment(SD, FG, last_segment.end_room)
                SD.remove_SD_in_segment(segment)

                log.debug("%sBS to JB: %s to %s%s", CONTINUE, segment.start_room, segment.end_room, RESET)

                return [segment], SD, FG #terminate, return this copy of SD and FG
            except RuntimeError as e:
                pass

    else:
        raise ValueError(f"last_segment was not BranchRoomPath")

    log.debug("%sFAILED BRANCH AFTER %s to %s%s", FAIL, last_segment.start_room, last_segment.end_room, RESET)
    raise RuntimeError(f"{ERROR}Failed to generate Branch Segment{RESET}")

def try_cap_with_J_branch(SD: SourceDestinationHandler, FG: FlowGraphHandler, branch_segment: BranchSegment):
    segment = john_segment(SD, FG, branch_segment.end_room)
    SD.remove_SD_in_segment(segment)

    log.debug("%sJ from BE: %s to %s%s", CONTINUE, segment.start_room, segment.end_room, RESET)

    return [branch_segment, segment], SD, FG #terminate, return this copy of SD and FG

def generate_level_recursive_between_branch(SD: SourceDestinationHandler, FG: FlowGraphHandler, last_segment: LevelSegment, branch_count: int, min_branch_count: int):
    SD = SD.copy() 
    FG = FG.copy()

    SD.remove_SD_in_segment(last_segment)

    segments = []

    #typecast end room to BranchRoomPath
    #check branch count again in case we want to immediately add a john
    #but go ahead anyways if we cant end with J

    can_end_with_J = len(SD.J) > 0

    if (type(last_segment.end_room) == BranchRoomPath and (branch_count < min_branch_count or not can_end_with_J)):
        for between_branch_segment in between_branch_segments(SD, FG, last_segment.end_room):

            log.debug("%sTRY TW: %s to %s%s", CONTINUE, between_branch_segment.start_room, between_branch_segment.end_room, RESET)
            
            try: 
                next_segments, new_SD, new_FG = generate_level_recursive_branch(SD, FG, last_segment=between_branch_segment, branch_count=branch_count,min_branch_count=min_branch_count)
                segments = []
                segments.append(between_branch_segment)
                segments.extend(next_segments)

                return segments, new_SD, new_FG
            except RuntimeError as e:
                pass

            log.debug("%sDUMP TW: %s to %s%s", FAIL, between_branch_segment.start_room, between_branch_segment.end_room, RESET)
    else:
        pass

    #could not increase branch count, try capping with J
    try:

        log.debug("Try BE to J")
        
        segment = john_segment(SD, FG, last_segment.end_room)
        SD.remove_SD_in_segment(segment)

        log.debug("%sBE to J: %s to %s%s", CONTINUE, segment.start_room, segment.end_room, RESET)

        return [segment], SD, FG #terminate, return this copy of SD and FG
    except RuntimeError as e:
        pass

    log.debug("%sFAILED TW AFTER %s to %s%s", CONTINUE, last_segment.start_room, last_segment.end_room, RESET)
    raise RuntimeError(f"{ERROR}Failed to generate Between Branch Segment{RESET}")


