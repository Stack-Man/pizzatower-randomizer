#Author: Stack Man
#Date: 2/11/2026
import json
import json_to_objects as jto

def test_parse_all():
    
    #filenames = ["johngutter", "ancientcheese", "bloodsauce", "crustcove", "deepdish9", "fastfoodsaloon"]
    filenames = ["pizzascape", "wasteyard", "funfarm", "oreganodesert"]
    all_rooms = []
    
    for f in filenames:
        full = "datafiles/json/" + f + ".json"
        
        new_rooms = test_parse(full)
        
        print("ROOMS  OF ", f)
        print("========================")
        print_rooms(new_rooms)
        
        all_rooms.extend(new_rooms)
    
    

def test_parse(filename):

    with open(filename, "r") as f:
        file = json.load(f)
        
        rooms = jto.json_to_rooms(file)

        return rooms
    
    print("failed load of ", filename)
    
    return []

def print_rooms(rooms):
    for room in rooms:
        room.print_stats()

test_parse_all()