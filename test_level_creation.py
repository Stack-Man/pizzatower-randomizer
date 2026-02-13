import json_to_objects as jto
import layer_traversal as lt
import layer_creation as lc
import json

def test_parse_all(filenames):
    
    all_rooms = []
    
    for f in filenames:
        full = "datafiles/json/" + f + ".json"
        
        new_rooms = test_parse(full)
        all_rooms.extend(new_rooms)
    
    TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE = lc.rooms_to_layers(all_rooms)
        
    #draw_tree(TW)
        
    levels = []
    
    for f in filenames:
        new_level = lt.create_level(TW, OW_NPT, OW_PT, BS, BE, E, EBS, J, JBE) 
        print_level(new_level)
        
        levels.append(new_level)
        

def test_parse(filename):

    with open(filename, "r") as f:
        file = json.load(f)
        
        rooms = jto.json_to_rooms(file)

        return rooms
    
    print("failed load of ", filename)
    
    return []

def print_level(level):
    
    print("LEVEL: ")
    
    for segment in level.segments:
        print(      "seg: ", str(segment))

print("JOHNGUTTER")
print("==========")
#test_parse_all(["johngutter"])

print("")
print("")
print("ANCIENTCHEESE")
print("==========")
#test_parse_all(["ancientcheese"])

#this combination's inclusion causes level creation to fail
#maybe less about these two specifically and more
#so the the coincidental pathing it takes when these two are there?

#fails even when there are many BE end options, not just ruins_11
#TODO: dive deeper into bridge oneway, is there a shared failure point?
#could it be the branch start point?

print("")
print("")
print("JOHNGUTTER & ANCIENTCHEESE")
print("==========")
test_parse_all(["johngutter", "ancientcheese"]) 

#these two are fine though
#test_parse_all(["bloodsauce", "ancientcheese"])
#test_parse_all(["bloodsauce", "johngutter"])

#this is also fine
#test_parse_all(["johngutter", "bloodsauce", "deepdish9", "fastfoodsaloon"]) 

#this fails
#test_parse_all([ "ancientcheese", "bloodsauce", "deepdish9", "johngutter", "fastfoodsaloon"])

#this also fails
#test_parse_all(["johngutter", "ancientcheese", "bloodsauce", "deepdish9", "fastfoodsaloon"])

#TODO: this causes A not found in G
#test_parse_all(["crustcove"]) 

