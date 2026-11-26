from level_generate import generate_levels, get_SD_FG
from settings import TraversalMode, GrowthMode
from json_parse import FILENAMES
from level_randomize import randomize_SD_FG, set_seed
from json_source_destination import SourceDestinationHandler

from profiler import profile_test#, profiler
import pstats

import logging as log

fn = ["johngutter", "ancientcheese", "bloodsauce", "pizzascape",
        "fastfoodsaloon", "wasteyard", "funfarm", "oreganodesert"]

traverse = TraversalMode.MATCHING_PERFECT

def test_randomize():

    for i in range(0, 2):
        log.debug("%s:", i)

        set_seed(0)

        SD, FG = get_SD_FG(fn, traverse)


        log.debug("PRE %s:", i)
        #print_SD(SD)

        
        randomize_SD_FG(SD, FG)

        log.debug("POST %s:", i)
        #print_SD(SD)


def print_SD(SD: SourceDestinationHandler):

    lists = [SD.E, SD.EB, SD.J, SD.JB, SD.BA, SD.BS, SD.BE]

    for L in lists:
        log.debug("     List:")
        for x in L:
            log.debug("         %s", x.name)



#test_randomize() #test with inner profiler
#pstats.Stats(profiler).strip_dirs().sort_stats("cumulative").print_stats(40)

profile_test(test_randomize, logging = True)
#profile_test_restricted(test_randomize, "bridge_branch_room_room", logging = True)