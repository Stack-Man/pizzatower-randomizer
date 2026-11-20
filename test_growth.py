#Author: Stack Man
#Date: 11/18/2026

from level_generate import generate_levels
from level_grow import grow_levels
from settings import get_growth_settings, TraversalMode
from level_objects import Level
from graph_create import FlowGraphHandler
from graph_objects import PathEdge, PathList

from perf_counter import print_perf

fn = ["johngutter", "ancientcheese"]

import log_config
import logging as log


def test_growth():
    levels, FG = generate_levels(fn = fn, traversal_mode=TraversalMode.MATCHING_PERFECT)

    log.debug("Generated %i levels", len(levels))
    log.debug("Try Grow %i Levels", len(levels))

    #print_all_path_lists(FG)

    grown_levels = grow_levels(levels, FG, get_growth_settings())

    log.debug("Grew %i levels", len(grown_levels))

    print_levels(grown_levels)

    print_perf()

def print_levels(levels: list[Level]):
    i = 0

    for level in levels:
        i += 1
        log.debug("Level %i:", i)
        log.debug(str(level))

def print_all_path_lists(FG: FlowGraphHandler):

    for U, V in FG.edges():
        obj = FG.get_edge_data(U, V)["object"]

        if (type(obj) == PathEdge):

            print_path_list(obj.TW)
            print_path_list(obj.OW)
            print_path_list(obj.PT)
            print_path_list(obj.NPT)

def print_path_list(PL: PathList):
    msg = str(PL)

    if (msg != ""):
        log.debug("paths: " + str(PL))

test_growth()