#Author: Stack Man
#Date: 11/1/2026
#Interface for reading JSON from filenames and returning as Room objects

import json
from json_to_objects import json_to_rooms
from settings import *
from colors import ERROR, RESET, CAUTION, WARNING

FILENAMES = ["johngutter", "ancientcheese", "bloodsauce", "pizzascape",
            "fastfoodsaloon", "wasteyard", "funfarm", "oreganodesert", 
            "crustcove", "deepdish9", "gnomeforest", "golf",
            "ohshit", "freezer", "peppibotfactory", "thepigcity",
            "dontmakeasound", "pizzascare", "war", 
            "crumblingtowerofpizza", "trickytreat", "tutorial", "tutorial_noise"]

def parse_json_to_rooms_all(filenames):
    if (not JSON_ROOMS_ALLOW_BRANCH_ROOMS):
        print(f"{WARNING}WARNING: IGNORING BRANCH ROOMS IN PARSE!{RESET}")
    if (not JSON_DOORS_ALLOW_TAXI_OR_ROCKET_DOORS):
        print(f"{WARNING}WARNING: IGNORING TAXI AND ROCKET DOORS IN PARSE!{RESET}")
    if (not JSON_DOORS_ALLOW_LOOP_DOORS):
        print(f"{WARNING}WARNING: IGNORING LOOP DOORS IN PARSE{RESET}")
    if (not JSON_ROOMS_ALLOW_NO_TRANSITION_ROOMS):
        print(f"{CAUTION}CAUTION: IGNORING NO TRANSITION ROOMS IN PARSE{RESET}")
    if (not JSON_ROOMS_ALLOW_LOOP_ROOMS):
        print(f"{CAUTION}CAUTION: IGNORING LOOP ROOMS IN PARSE{RESET}")
    
    all_rooms = []
    
    for f in filenames: 
        filename = "json/" + f + ".json"
        new_rooms = parse_json_to_rooms(filename)
        all_rooms.extend(new_rooms)

    return all_rooms

def parse_json_to_rooms(filename):
    with open(filename, "r") as f:
        file = json.load(f)
        
        rooms = json_to_rooms(file)

        return rooms
    
    print(f"{ERROR}ERROR: failed to open file {filename}{RESET}")
    
    return []