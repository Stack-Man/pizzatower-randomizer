#This file contains settings parameters related to level generation

from enum import Enum

#JSON

#a "loop" door is any transition that loops to itself in the standard loop, such as Gerome doors
JSON_DOORS_ALLOW_LOOP_DOORS = True 

JSON_DOORS_ALLOW_TAXI_OR_ROCKET_DOORS = True

#ignore rooms that have only one transition (and aren't Pillar John or Entrance rooms)
JSON_ROOMS_ALLOW_LOOP_ROOMS = False

#ignore rooms that have no transitions (secrets)
JSON_ROOMS_ALLOW_NO_TRANSITION_ROOMS = False

#ignore rooms that are branches
JSON_ROOMS_ALLOW_BRANCH_ROOMS = True

#GRAPH
#TraversalMode: How transitions between rooms can connect

#MODE: matching perfect
#Match transitions with the same type and consistent directions
             
#MODE: matching directional
#Match transitions that have consistent directions, but possibly different types

#MODE: arbitrary no turnarounds
#Match transitions in any way, but don't allow left/left, right/right, up/up, or down/down
    
#MODE: arbitrary no restrictions
#Match transitions in any way

class TraversalMode(Enum):
    NONE = 0
    MATCHING_PERFECT = 1
    MATCHING_DIRECTIONAL = 2
    ARBITRARY_NO_TURNAROUNDS = 3
    ARBITRARY_NO_RESTRICTIONS = 4
    DEBUG = 5

GRAPH_TRAVERSAL_MODE = TraversalMode.MATCHING_PERFECT

#LEVEL
#GrowthMode: How new rooms are added to existing levels
#LEVEL_GROWTH_MODE: How new rooms are distributed between levels
#SEGMENT_GROWTH_MODE: How new rooms are distributed between segments within a single level
#SEGMENT_INNER_GROWTH_MODE: How new rooms are distributed between rooms within a single segment

#EQUAL_LENGTH: Growth targets an equal number of total rooms amongst levels/segments (smallest first)
#EQUAL_GROWTH: Growth targets an equal number of added rooms amongst levels/segments (fewest added rooms first)
#ORDERED_EQUAL_ATTEMPTS: Levels/Segments get one growth each before any repeats (form a queue)
#ORDERED_MAXIMUM_UNEVEN: Level/Segment is grown as much as possible before continuing (fatten first in queue)
#RANDOM: randomly choose a level/segment to grow after each growth

class GrowthMode(Enum):
    EQUAL_LENGTH = 0
    EQUAL_GROWTH = 1
    ORDERED_EQUAL_ATTEMPTS = 2
    ORDERED_MAXIMUM_UNEVEN = 3
    RANDOM = 4

LEVEL_GROWTH_MODE = GrowthMode.EQUAL_LENGTH
SEGMENT_GROWTH_MODE = GrowthMode.EQUAL_LENGTH
SEGMENT_INNER_GROWTH_MODE = GrowthMode.EQUAL_LENGTH

#GrowthQueueMode: How rooms in ORDERED growth modes form a queue (ORDERED_EQUAL_ATTEMPTS or ORDERED_MAXIMUM_UNEVEN)

#BALANCED: evenly distribute levels/segments based on their original position
#RANDOM: randomly distribute levels/segments in the queue (may be randomly front or back loaded)
#FRONT_LOADED: levels/segments earlier get priority
#BACK_LOADED: levels/segments later get priority

class GrowthQueueMode(Enum):
    BALANCED = 0
    RANDOM = 1
    FRONT_LOADED = 2
    BACK_LOADED = 3

LEVEL_ORDERED_GROWTH_QUEUE_MODE = GrowthQueueMode.BALANCED
SEGMENT_ORDERED_GROWTH_QUEUE_MODE = GrowthQueueMode.BALANCED
SEGMENT_INNER_ORDERED_GROWTH_QUEUE_MODE = GrowthQueueMode.BALANCED

#InnerGrowthRecursionMode: When new rooms are added between rooms in a segment, when should we allow growth between those new rooms?

#NEVER: never try to add new rooms between added rooms
#IMMEDIATE: new rooms are treated the same as existing rooms immediately
#AFTER_EQUAL_ATTEMPTS: for ORDERED_EQUAL_ATTEMPTS, after each room pair has been tried at least once, then allow new rooms between added rooms

class InnerGrowthRecursionMode(Enum):
    NEVER = 0
    IMMEDIATE = 1
    AFTER_EQUAL_ATTEMPTS = 2

GROWTH_RECURSION_MODE = InnerGrowthRecursionMode.NEVER

class GrowthSettings():
    def __init__(self, growth_mode: GrowthMode, queue_mode: GrowthQueueMode):
        self.growth_mode = growth_mode
        self.queue_mode = queue_mode

class LevelGrowthSettings():
    def __init__(self, level_settings: GrowthSettings, segment_settings: GrowthSettings, inner_segment_settings: GrowthSettings, inner_recursion: InnerGrowthRecursionMode):
        self.level = level_settings
        self.segment = segment_settings
        self.inner_segment = inner_segment_settings
        self.inner_recursion = inner_recursion

def get_growth_settings():
    level = GrowthSettings(LEVEL_GROWTH_MODE, LEVEL_ORDERED_GROWTH_QUEUE_MODE)
    segment = GrowthSettings(SEGMENT_GROWTH_MODE, SEGMENT_ORDERED_GROWTH_QUEUE_MODE)
    inner = GrowthSettings(SEGMENT_INNER_GROWTH_MODE, SEGMENT_INNER_ORDERED_GROWTH_QUEUE_MODE)

    return LevelGrowthSettings(level, segment, inner, GROWTH_RECURSION_MODE)


    