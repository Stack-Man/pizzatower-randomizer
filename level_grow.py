#Author: Stack Man
#Date: 11/18/2026

#Add rooms to already existing room segments

from level_objects import Level, TwowaySegment, BranchSegment, BaseRoomPath, RoomSelection
from json_source_destination import SourceDestinationHandler
from graph_from_rooms import FlowGraphHandler
from settings import GrowthMode, GrowthQueueMode, InnerGrowthRecursionMode, GrowthSettings, LevelGrowthSettings
from enums import TraversalType
from level_bridge import bridge_rp_rp
from perf_counter import start_perf, end_perf, PerfType
import logging as log

#TODO: add oneway segment growth for War/CTOP (Change their TW segment to new OW segment?)

def grow_levels(levels: list[Level], FG: FlowGraphHandler, growth_settings: LevelGrowthSettings):

    #TODO: use growth_settings to iterate over levels
    grown_levels = []

    for level in levels:
        log.debug("Growing level %s: ", level.segments[0].start_room.room.name)
        start_perf(PerfType.GROWTH)
        grown_level = grow_level(level, FG, growth_settings)
        grown_levels.append(grown_level)
        time = end_perf(PerfType.GROWTH)
        log.debug("Time: (%i)", time)
    
    return levels

def grow_level(level: Level, FG: FlowGraphHandler, growth_settings: LevelGrowthSettings):

    grown_segments = []

    #TODO: use growth_settings to iterate over segments
    #TODO: can't just iterate over segments, have to yield or somethin so we can switch between level segments
    for segment in level.segments:

        log.debug("     Growing segment %s:", str(segment))
        
        grown_segment = grow_segment(segment, FG, growth_settings)
        grown_segments.append(grown_segment)
    
    return Level(grown_segments)

def grow_segment(segment: TwowaySegment | BranchSegment, FG: FlowGraphHandler, growth_settings: LevelGrowthSettings):

    if (type(segment) == TwowaySegment):
        return grow_twoway_segment(segment, FG, growth_settings)
    elif (type(segment) == BranchSegment):
        return grow_branch_segment(segment, FG, growth_settings)
    else:
        raise TypeError(f"segment was not TwowaySegment or BranchSegment but {type(segment)}")

def grow_twoway_segment(segment: TwowaySegment, FG: FlowGraphHandler, growth_settings: LevelGrowthSettings):
    old_rooms = [segment.start_room]
    old_rooms.extend(segment.between_rooms.rooms)
    old_rooms.append(segment.end_room)

    rooms = grow_inner_segment(old_rooms, FG, TraversalType.ANY, growth_settings)

    new_selection = RoomSelection(rooms[1: -1]) #all rooms except first and last

    return TwowaySegment(segment.start_room, segment.end_room, new_selection)

def grow_branch_segment(segment: BranchSegment, FG: FlowGraphHandler, growth_settings: LevelGrowthSettings):
    old_rooms_PT = [segment.start_room]
    old_rooms_PT.extend(segment.pt_between_rooms.rooms)
    old_rooms_PT.append(segment.end_room)

    rooms_PT = grow_inner_segment(old_rooms_PT, FG, TraversalType.PIZZATIME, growth_settings)

    old_rooms_NPT = [segment.end_room]
    old_rooms_NPT.extend(segment.npt_between_rooms.rooms)
    old_rooms_NPT.append(segment.start_room)

    rooms_NPT = grow_inner_segment(old_rooms_NPT, FG, TraversalType.NOTPIZZATIME, growth_settings)

    PT_selection = RoomSelection(rooms_PT[1: -1])
    NPT_selection = RoomSelection(rooms_NPT[1: -1])

    return BranchSegment(segment.start_room, segment.end_room, PT_selection, NPT_selection)

def every_two(list):
    i = 0

    while (i + 1 < len(list)):
        yield list[i], list[i + 1]
        i += 1
        
def grow_inner_segment(old_rooms: list[BaseRoomPath], FG:FlowGraphHandler, traversal_type: TraversalType, growth_settings: LevelGrowthSettings):
    rooms = []

    rooms.append(old_rooms[0])
    
    for A, B in every_two(old_rooms):

        log.debug("         Growing between rooms %s and %s:", str(A), str(B))

        try:
            bridge = bridge_rp_rp(A, B, FG, TraversalType.ANY, force_extension = True)
            rooms.extend(bridge.rooms)

            log.debug("             Grew with %s:", str(bridge))

        except Exception as e:
            log.debug("             " + str(e))
            pass

        #only append B because A was added last loop
        rooms.append(B)

    log.debug("         Grew from %i to %i", len(old_rooms), len(rooms))



    log.debug("             old rooms: %s", ">".join(room.room.name for room in old_rooms))
    log.debug("             new rooms: %s", ">".join(room.room.name for room in rooms))



    return rooms

