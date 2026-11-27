from json_parse import FILENAMES, parse_json_to_rooms_all
from json_objects import Room
from enums import RoomType, BranchType, StartExitType

from level_room_path_generator import branch_room_path 

import logging as log
from profiler import profile_test


#wasteyard graveyard_3 is not marked as a branch room because it has a pizzatime start but no notpizzatime exclusive exit, using a type FORCED_BRANCH_ANY
#ruins_1 has an unhandled key loop, marking B and C as "loop" for now
#saloon2 was not marked as a branch room due to one door not being exclusive, using type FORCED_BRANCH_START
#freezer_4 was not marked as branch room due to one door not beign exclusive, using type FORCED_BRANCH_START
#street_jail is double-booked without loop doors (taxi, taxistart, door)
#trickytreat_1 is double-booked without loop doors (box up, hallway down, door)

fn = FILENAMES

def test_parse_all():
    all_rooms = parse_json_to_rooms_all(fn)

    for room in all_rooms:
        room : Room

        if (room.room_type == RoomType.NORMAL and len(room.doors) >= 3):
            log.debug("Possible Branch Candidate: %s", room)

    to_test = ["entrance_7", "ruin_3", "dungeon_7"]

    for room in all_rooms:
        room : Room

        if (room.name in to_test and room.branch_type != BranchType.NONE):
        #if (room.branch_type != BranchType.NONE):

            log.debug("Branch %s of type %s", room, room.branch_type)
            log.debug("     As Start: ")

            for rp in branch_room_path(room, StartExitType.START):
                log.debug("         %s Branch: %s NPT: %s PT: %s", rp.room, rp.branch_door, rp.npt, rp.pt)


            log.debug("     As Exit: ")

            for rp in branch_room_path(room, StartExitType.EXIT):
                log.debug("         %s Branch: %s NPT: %s PT: %s", rp.room, rp.branch_door, rp.npt, rp.pt)
        

profile_test(test_parse_all)