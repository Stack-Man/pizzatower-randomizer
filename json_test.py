import json
from json_to_objects import json_to_rooms
from objects import Room, Path, Door
from enums import DoorType, DoorDir, RoomType

#wasteyard graveyard_3 is not marked as a branch room because it has a pizzatime start but no notpizzatime exclusive exit, using a type FORCED_BRANCH_ANY
#ruins_1 has an unhandled key loop, marking B and C as "loop" for now
#saloon2 was not marked as a branch room due to one door not being exclusive, using type FORCED_BRANCH_START
#freezer_4 was not marked as branch room due to one door not beign exclusive, using type FORCED_BRANCH_START
#street_jail is double-booked without loop doors (taxi, taxistart, door)
#trickytreat_1 is double-booked without loop doors (box up, hallway down, door)

def test_parse_all():

    filenames = ["johngutter", "ancientcheese", "bloodsauce", "pizzascape",
                 "fastfoodsaloon", "wasteyard", "funfarm", "oreganodesert", 
                 "crustcove", "deepdish9", "gnomeforest", "golf",
                 "ohshit", "freezer", "peppibotfactory", "thepigcity",
                 "dontmakeasound", "pizzascare", "war", 
                 "crumblingtowerofpizza", "trickytreat", "tutorial", "tutorial_noise"]

    filenames = ["funfarm"]

    all_rooms = []
    
    for f in filenames: 
        filename = "json/" + f + ".json"

        new_rooms = test_parse(filename)
        
        print("ROOMS  OF ", f)
        print("========================")
        print_rooms(new_rooms)
        
        all_rooms.extend(new_rooms)


    #print_unique_path_types(all_rooms)
    
    

def test_parse(filename):


    with open(filename, "r") as f:
        file = json.load(f)
        
        rooms = json_to_rooms(file)

        return rooms
    
    print("failed load of ", filename)
    
    return []

def print_rooms(rooms):
    for room in rooms:
        room.print_stats()

        #room.print_doors()

        room.print_paths_extended()

def print_unique_path_types(rooms: list[Room]):

    path_types = {}

    for room in rooms:

        if (not can_be_double_booked(room)):
            continue

        print(f"{room.name}:")  

        for path in room.paths:

            start = path.start_door
            exit = path.exit_door

            path_type = (start.door_type, start.door_dir, exit.door_type, exit.door_dir)

            if (start.door_type == exit.door_type and start.door_dir == exit.door_dir):
                continue

            if (path_type not in path_types):
                path_types[path_type] = 1
            else:
                path_types[path_type] = path_types[path_type] + 1

            continue

    for room in rooms:
    
            if (can_be_double_booked(room)):
                continue

            for path in room.paths:
    
                start = path.start_door
                exit = path.exit_door
    
                path_type = (start.door_type, start.door_dir, exit.door_type, exit.door_dir)
    
                if (start.door_type == exit.door_type and start.door_dir == exit.door_dir):
                    continue
    
                if (path_type  in path_types):
                    path_types[path_type] = path_types[path_type] + 1

                continue

    #for key, value in path_types.items():
        #print_path_type(key, value)

    for key, value in sorted(path_types.items(), key=lambda item: item[1], reverse=True):
        print_path_type(key, value)

    return

def print_path_type(path_type: tuple[DoorType, DoorDir, DoorType, DoorDir], count: int):
    start_type = door_type_to_string(path_type[0])
    exit_type = door_type_to_string(path_type[2])

    start_dir = door_dir_to_string(path_type[1])
    exit_dir = door_dir_to_string(path_type[3])

    msg = start_type + " " + start_dir + " -> " + exit_type + " " + exit_dir + " : " + str(count)

    print(msg)

def door_type_to_string(type: DoorType):

    match type:
        case DoorType.ANY: return "Any"
        case DoorType.BOX: return "Box"
        case DoorType.DOOR: return "Door"
        case DoorType.HORIZONTAL: return "Hall"
        case DoorType.VERTICAL: return "Vert"
        case DoorType.LEVELDOOR: return "Entr"
        case DoorType.SECRET: return "Secret"
        case DoorType.ROCKET: return "Rocket"
        case DoorType.TAXI: return "Taxi"

    return "FAIL"
        
def door_dir_to_string(type: DoorDir):

    match type:
        case DoorDir.NONE: return ""
        case DoorDir.UP: return "U"
        case DoorDir.DOWN: return "D"
        case DoorDir.LEFT: return "L"
        case DoorDir.RIGHT: return "R"

    return "FAIL"

def can_be_double_booked(room: Room):
    #a double bookable room must have at least 2 paths, three transition types, and 2 paths whose starts or ends don't match
    #and must be a normal room

    room_type = room.room_type

    if (room_type is not RoomType.NORMAL):
        return False

    paths_count = len(room.paths)

    if (paths_count < 2):
        return False

    transition_type_count = count_transition_types(room.paths)

    if (transition_type_count < 3):
        return False

    has_two_paths_with_non_matching_starts_or_ends = check_path_transition_match(room.paths)

    if (has_two_paths_with_non_matching_starts_or_ends):
        return True

    return False

def count_transition_types(paths: list[Path]):

    transition_types = []

    for path in paths:

        start_type = (path.start_door.door_type, path.start_door.door_dir)

        if (start_type not in transition_types):
            transition_types.append(start_type)

        exit_type = (path.exit_door.door_type, path.exit_door.door_dir)
        
        if (exit_type not in transition_types):
            transition_types.append(exit_type)

    return len(transition_types)

def check_path_transition_match(paths: list[Path]):

    for path_A in paths:

        for path_B in paths:

            if (path_A is path_B):
                continue

            A_start = path_A.start_door
            A_exit = path_A.exit_door

            B_start = path_B.start_door
            B_exit = path_B.exit_door

            #if any two paths DONT have a shared start type or a shared exit type
            if ( (A_start.door_type is not B_start.door_type or
                 A_start.door_dir is not B_start.door_dir) and 
                 (A_exit.door_type is not B_exit.door_type or
                 A_exit.door_dir is not B_exit.door_dir) ):

                #entrances cannot be double booked
                if (A_start.door_type is not DoorType.LEVELDOOR and A_exit.door_type is not DoorType.LEVELDOOR 
                    and B_start.door_type is not DoorType.LEVELDOOR and B_exit.door_type is not DoorType.LEVELDOOR):
                    return True

    return False

test_parse_all()