from level_generate import generate_levels
from settings import TraversalMode, get_growth_settings
from json_parse import FILENAMES

from profiler import profile_test

def test_randomize():
    levels = generate_levels(
        fn= FILENAMES, 
        traversal_mode= TraversalMode.MATCHING_PERFECT, 
        growth_settings= get_growth_settings(),
        seed = 1 
        )

profile_test(test_randomize, logging = True)