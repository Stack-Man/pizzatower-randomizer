#Author: Stack Man
#Date: 11/12/2026

from level_generate_recursive import generate_levels_recursive_all
from main import get_SD_FG
from level_objects import Level
from json_parse import FILENAMES

def test_generate():
    #SD, FG = get_SD_FG(["johngutter", "pizzascape"]) 
    SD, FG = get_SD_FG(FILENAMES) 
    levels = generate_levels_recursive_all(SD, FG)

    print_levels(levels)

def print_levels(levels: list[Level]):

    for level in levels:
        print(f"Level: {level.name}")
        print(f"    {level}")

test_generate()