from level_generate import generate_levels
from settings import TraversalMode, get_growth_settings
from json_parse import FILENAMES

from profiler import profile_test#, profiler
import pstats


def test_randomize():
    levels = generate_levels(
        fn= FILENAMES, 
        traversal_mode= TraversalMode.MATCHING_PERFECT, 
        growth_settings= get_growth_settings(),
        seed = 1 
        )

#test_randomize() #test with inner profiler
#pstats.Stats(profiler).strip_dirs().sort_stats("cumulative").print_stats(40)

profile_test(test_randomize, logging = False)
#profile_test_restricted(test_randomize, "bridge_branch_room_room", logging = True)