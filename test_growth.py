#Author: Stack Man
#Date: 11/18/2026

from level_generate import generate_levels
from level_grow import grow_levels
from settings import get_growth_settings, TraversalMode
from level_objects import Level

from perf_counter import print_perf

fn = ["johngutter"]

import log_config
import logging as log


def test_growth():
    levels, FG = generate_levels(fn = fn, traversal_mode=TraversalMode.MATCHING_PERFECT)

    log.debug("Generated %i levels", len(levels))
    log.debug("Try Grow %i Levels", len(levels))

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

test_growth()