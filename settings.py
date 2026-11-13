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