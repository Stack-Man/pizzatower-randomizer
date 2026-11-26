#Author: Stack Man
#Date: 11/18/2026

from level_generate import generate_base_levels
from level_segment_generator import ej_or_ejb_segment_forced
from level_grow import grow_levels, grow_levels_track_size
from settings import GrowthMode, TraversalMode
from level_objects import Level
from graph_create import FlowGraphHandler
from graph_objects import PathEdge, PathList

from perf_counter import print_perf
from json_parse import FILENAMES

from level_generate import get_SD_FG



import log_config
import logging as log
from perf_counter import get_perf, PerfType
from profiler import profile_test

grow = GrowthMode.EQUAL_LENGTH
traverse = TraversalMode.MATCHING_PERFECT

fn = ["johngutter", "ancientcheese", "bloodsauce", "pizzascape",
        "fastfoodsaloon", "wasteyard", "funfarm", "oreganodesert"]

fn = FILENAMES

def test_generate():
    levels, FG = generate_base_levels(fn = fn, traversal_mode=traverse)
    log.debug("Generated %i levels in %s\n\n\n", len(levels), get_perf(PerfType.GEN))
    print_levels(levels)
    

def test_growth():
    levels, FG = generate_base_levels(fn = fn, traversal_mode=traverse)

    log.debug("Generated %i levels in %s\n\n\n", len(levels), get_perf(PerfType.GEN))
    log.debug("Generated %i levels in %s\n\n\n", len(levels), get_perf(PerfType.GEN))

    print_levels(levels)

    grown_levels = grow_levels_track_size(levels, FG, grow)

    print_levels(grown_levels)


def test_growth_forced(A: str, B: str):
    SD, FG = get_SD_FG(fn = fn, traversal_mode=traverse)

    level = level_generate_forced(FG, SD, A, B)

    grown_levels = grow_levels_track_size([level], FG, grow)

    print_levels(grown_levels)

    print_perf()

def level_generate_forced(FG, SD, A, B):

    segment = ej_or_ejb_segment_forced(FG, SD, A, B)

    return Level([segment])

def print_levels(levels: list[Level]):
    i = 0

    for level in levels:
        i += 1
        log.debug("Level %i: \n %s\n\n", i, str(level))

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


profile_test(test_growth, logging=True)
#profile_test(lambda: test_growth_forced("industrial_1", "freezer_escape1"), logging=True)