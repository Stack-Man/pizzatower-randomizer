#Author: Stack Man
#Date: 11/7/2026

from json_parse import parse_json_to_rooms_all, FILENAMES
from json_double_booking import identify_double_bookable_rooms

def test_double_booking():

    all_rooms = parse_json_to_rooms_all(FILENAMES)
    identify_double_bookable_rooms(all_rooms)

    return

test_double_booking()