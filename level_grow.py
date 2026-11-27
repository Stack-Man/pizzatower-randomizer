#Author: Stack Man
#Date: 11/25/2026

#Grow levels using custom growth settings
from json_objects import Room
from level_objects import Level, LevelSegment, TwowaySegment, BranchSegment, BaseRoomPath, RoomSelection, RoomPath
from graph_create import FlowGraphHandler
from level_clean_replenish import clean_selections
from enum import Enum
from enums import TraversalType
from level_bridge import bridge_rp_rp
from settings import GrowthMode
from perf_counter import start_perf, end_perf, PerfType

import random
import logging as log

def grow_levels_track_size(levels: list[Level], FG: FlowGraphHandler, mode: GrowthMode):

    old_size : dict[Level, int] = {}

    for L in levels:
        old_size[L] = len(L)

    grown_levels = grow_levels(levels, FG, mode)

    for L in grown_levels:
        log.debug("%s from %s to %s", L.segments[0].start_room.room, old_size[L], len(L))

    return grown_levels

def grow_levels(levels: list[Level], FG: FlowGraphHandler, mode: GrowthMode):
    start_perf(PerfType.GROWTH)

    grown_levels = grow_levels_match(levels, FG, mode)

    end_perf(PerfType.GROWTH)

    return grown_levels

def grow_levels_match(levels: list[Level], FG: FlowGraphHandler, mode: GrowthMode):

    match mode:
        case GrowthMode.EQUAL_GROWTH:
            return grow_levels_equal_growth(levels, FG)
        case GrowthMode.EQUAL_LENGTH:
            return grow_levels_equal_length(levels, FG)

    raise NotImplementedError(f"grow_levels not implemented for {mode}")

def grow_levels_equal_growth(levels: list[Level], FG: FlowGraphHandler):
    return grow_levels_template(levels, FG, every_level_once, random_unused_segment)

def grow_levels_equal_length(levels: list[Level], FG: FlowGraphHandler):
    return grow_levels_template(levels, FG, shortest_level_next, shortest_segment_next)

def grow_levels_template(levels: list[Level], FG: FlowGraphHandler, level_iterator, segment_iterator):
    #for each level, store which segments have been processed
    #reset once no segments have been unprocessed
    processed_segments : dict[Level, set[TwowaySegment | BranchSegment]] = {}

    #For each level, store which segments can no longer be grown
    filled_segments : dict[Level, set[TwowaySegment | BranchSegment]] = {}

    #For each segment, store which room pairs failed so they never repeat
    failed_pairs : dict[BranchSegment | TwowaySegment, set[tuple[BaseRoomPath, BaseRoomPath]]] = {}

    failed_levels : set[Level] = set()

    for L in level_iterator(levels, failed_levels):

        grew = False

        processed = processed_segments.setdefault(L, set())
        filled = filled_segments.setdefault(L, set())

        #until we grow a segment in L
        for S in segment_iterator(L.segments, processed, filled):

            failed = failed_pairs.setdefault(S, set())

            #until we grow a room pair in S
            #yield adjacent room pair and index of A
            #and if they're from the PT segment, unused if TW
            for A, B, iA, is_PT in random_room_pair(S, failed):

                grew = grow_between_room_pair(FG, L, S, A, B, iA, is_PT)

                #move to next L if grew
                if (grew):
                    break
                else:
                    #log.debug("Failed to grow between %s to %s", A.room.name, B.room.name)
                    failed.add((A, B))

            #move to next L if grew
            if (grew):
                break
            else:
                #log.debug("Failed to grow segment %s to %s", S.start_room.room.name, S.end_room.room.name)
                filled.add(S)

        #if not grew, then all S have failed to grow
        if not grew:
            log.debug("Failed to grow %s", L.segments[0].start_room.room.name)
            failed_levels.add(L)

    return levels

        
def every_level_once(levels: list[Level], failed_levels: set[Level]):
    random_order = levels.copy()
    random.shuffle(random_order)

    #grow until all levels fail to grow
    while (len(failed_levels) < len(levels)):
        for L in random_order:
            if L not in failed_levels:
                yield L

def shortest_level_next(levels: list[Level], failed_levels: set[Level]):

    by_smallest = sorted(levels, key = lambda x : len(x))

    #grow until all levels fail to grow
    while (len(failed_levels) < len(levels)):

        grew = False
        old_size = len(failed_levels)

        #yield shortest non failed level
        for L in by_smallest:

            if L not in failed_levels:

                yield L 

                #after yield we might have grown or failed with L
                #if size of failed increased, we didn't grow
                new_size = len(failed_levels)
                grew = new_size == old_size

                #if grew, break so we can resort
                #if not, continue to next shortest
                if (grew):
                    break

        #re-sort the list if we grew 
        if (grew):
            by_smallest = sorted(levels, key = lambda x : len(x))


def random_unused_segment(segments: list[TwowaySegment | BranchSegment], 
                          used_segments: set[TwowaySegment | BranchSegment], 
                          filled_segments: set[TwowaySegment | BranchSegment]):

    #start at random position in the list
    start = random.randint(0, len(segments) - 1) 
    i = start

    #until we run out of segments to try
    while (len(filled_segments) < len(segments)):

        #reset used when all are used
        if len(used_segments) == len(segments):
            used_segments.clear()
        
        #iterate over list until we find an unused segment
        while (segments[i] in used_segments or segments[i] in filled_segments):

            i += 1

            if (i >= len(segments)):
                i = 0

            if (i == start):
                break

        #mark the used segment and yield
        target = segments[i]
        used_segments.add(target)
        yield target

        #if we are still processing this loop, yielded segement must have been filled
        #filled_segments.add(target)

def shortest_segment_next(segments: list[TwowaySegment | BranchSegment], 
                          _ : set[TwowaySegment | BranchSegment], #used segments is irrelevant for shortest_next, ignore
                          filled_segments: set[TwowaySegment | BranchSegment]):

    if (len(filled_segments) == len(segments)):
        return

    #we only plan to grow one segment of level before breaking
    #so we only need to sort once
    #the first successful yield will exit the segment loop
    by_smallest = sorted(segments, key = lambda x : len(x))
    
    for S in by_smallest:

        if S not in filled_segments:

            yield S



def random_room_pair(segment: TwowaySegment | BranchSegment, failed_pairs: set[tuple[BaseRoomPath, BaseRoomPath]]):

    if (type(segment) == TwowaySegment):
        return random_room_pair_twoway(segment, failed_pairs)
    elif(type(segment) == BranchSegment):
        return random_room_pair_branch(segment, failed_pairs)
    else:
        raise NotImplementedError(f"random_room_pair not implemented for {type(segment)}")

def random_room_pair_twoway(segment: TwowaySegment, failed_pairs: set[tuple[BaseRoomPath, BaseRoomPath]]):

    rooms = [segment.start_room]
    rooms.extend(segment.between_rooms.rooms)
    rooms.append(segment.end_room)

    for A, B, iA, in random_unfailed_room_pair(rooms, failed_pairs):
        yield A, B, iA, False

def random_room_pair_branch(segment: BranchSegment, failed_pairs: set[tuple[BaseRoomPath, BaseRoomPath]]):
    #PT is end > between > start
    rooms_PT = [segment.end_room]
    rooms_PT.extend(segment.pt_between_rooms.rooms)
    rooms_PT.append(segment.start_room)

    #NPT is start > between > end
    rooms_NPT = [segment.start_room]
    rooms_NPT.extend(segment.npt_between_rooms.rooms)
    rooms_NPT.append(segment.end_room)

    #randomize which selection we traverse first
    first_rooms = rooms_PT
    first_is_PT = True
    second_rooms = rooms_NPT

    swap = random.randint(0, 1) == 1

    if (swap):
        second_rooms = rooms_PT
        first_rooms = rooms_NPT
        first_is_PT = False

    for A, B, iA, in random_unfailed_room_pair(first_rooms, failed_pairs):
        yield A, B, iA, first_is_PT

    for A, B, iA in random_unfailed_room_pair(second_rooms, failed_pairs):
        yield A, B, iA, not first_is_PT
    
def random_unfailed_room_pair(rooms: list[BaseRoomPath], failed_pairs: set[tuple[BaseRoomPath, BaseRoomPath]]):
    #-2 to exclude last room as a start and be within index range
    start = random.randint(0, len(rooms) - 2)
    i = start
    processed = 0

    #stop if we process all pairs, -1 to exclude the last room
    while (processed < len(rooms) - 1):

        A = rooms[i]
        B = rooms[i + 1]

        if (A, B) not in failed_pairs:
            yield A, B, i

        i += 1
        processed += 1

        #reset when index is = last room index
        if (i >= len(rooms) - 1):
            i = 0

        if (i == start):
            break

        
def grow_between_room_pair(FG: FlowGraphHandler, level: Level, segment: TwowaySegment | BranchSegment, A: BaseRoomPath, B: BaseRoomPath, iA: int, is_PT: bool):

    traversal_type = get_traversal_type(segment, is_PT)

    try:
        #get bridge (if possible)
        bridge = bridge_rp_rp(A, B, FG, traversal_type)

        #replace segment's room selection with new selection, including bridge
        #account for iA and iB offset from start/end room index vs selection being just between
        place_selection_within_selection(segment, bridge, iA, is_PT)

        #Clean up FG
        clean_selections(FG, selections=[bridge])

        log.debug("Grew %s: %s to %s with %s:", str(level.segments[0].start_room), A.room, B.room, str(bridge))

        return True #return True if successful grow

    except RuntimeError as e:
        #log.debug(e)

        return False

def get_traversal_type(segment, is_PT):
    if (type(segment) == TwowaySegment):
        return TraversalType.ANY
    elif (type(segment) == BranchSegment):
        if (is_PT):
            return TraversalType.PIZZATIME
        else:
            return TraversalType.NOTPIZZATIME
    else:
        raise NotImplementedError(f"get_traversal_type not implemented for {type(segment)}")

def place_selection_within_selection(segment: TwowaySegment | BranchSegment, bridge: RoomSelection, iA: int, is_PT: bool):

    if (type(segment) == TwowaySegment):
        place_selection_within_twoway(segment, bridge, iA)
    elif(type(segment) == BranchSegment):
        place_selection_within_branch(segment, bridge, iA, is_PT)
    else:
        raise NotImplementedError(f"place_selection_within_selection not implemented for {type(segment)}")

def place_selection_within_twoway(segment: TwowaySegment, bridge: RoomSelection, iA: int):

    #iA and iB are indexes of the bridged room pair
    #within [segment.start, [segment.between], segment.end]
    #we must adjust the indexes to get the positions within segment.between instead

    old_rooms = segment.between_rooms.rooms
    new_rooms = splice_selection(old_rooms, bridge, iA)

    segment.between_rooms = RoomSelection(new_rooms)

def place_selection_within_branch(segment: BranchSegment, bridge: RoomSelection, iA: int, is_PT: bool):

    old_rooms = segment.pt_between_rooms.rooms if is_PT else segment.npt_between_rooms.rooms
    new_rooms = splice_selection(old_rooms, bridge, iA)

    if (is_PT):
        segment.pt_between_rooms = RoomSelection(new_rooms)
    else:
        segment.npt_between_rooms = RoomSelection(new_rooms)

def splice_selection(old_rooms: list[RoomPath], bridge: RoomSelection, iA: int):

    #imagine a list [A, B, C, D] and old_rooms [B, C]
    #iA and iB are indexes of the first list
    #iA = 0, and iB = 1
    #[] + [B, C], [] = stop at and exclude id 0 (iA), [B, C] include and continue from id 0 (iB - 1)
    #and so on...
    
    front_rooms = old_rooms[:iA] #stop is exclusive, exclude index iA
    bridge_rooms = bridge.rooms
    back_rooms = old_rooms[iA:] #start is inclusive, exclude iB - 1, iB = iA + 1 so iB - 1 == iA

    new_rooms = []
    new_rooms.extend(front_rooms)
    new_rooms.extend(bridge_rooms)
    new_rooms.extend(back_rooms)

    return new_rooms

