import log_config
import logging as log
from perf_counter import print_perf
import cProfile
import pstats


def profile_test(func, logging = True):
    if (not logging):
        log.disable()
    profiler = cProfile.Profile()

    profiler.enable()
    func()
    profiler.disable()

    # Sort results by cumulative time spent in each function
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(15)  # Print top 10 slowest functions

    print_perf()

