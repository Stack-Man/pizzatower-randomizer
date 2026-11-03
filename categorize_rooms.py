#Author: Stack Man
#Date: 11/1/2026

#Categorize, identify, and mark Rooms and Paths

from objects import Room, Path
from enums import RoomType, BranchType
from colors import ERROR, RESET
from double_booking import identify_double_bookable_rooms


def categorize_rooms(rooms: list[Room]):
    normal, branch, entrance, john, entrance_branch, john_branch = categorize_rooms_by_type(rooms)

    #identify and mark double-bookable rooms
    identify_double_bookable_rooms(normal)

    return normal, branch, entrance, john, entrance_branch, john_branch

def categorize_rooms_by_type(rooms: list[Room]):

    normal = []
    branch = []
    entrance = []
    john = []
    entrance_branch = []
    john_branch = []

    for room in rooms:
        match room.room_type:
            case RoomType.NORMAL:
                normal.append(room)
            case RoomType.BRANCH:
                branch.append(room)
            case RoomType.ENTRANCE:
                if (room.branch_type is not BranchType.NONE):
                    entrance.append(room)
                else:
                    entrance_branch.append(room)
            case RoomType.JOHN:
                if (room.branch_type is not BranchType.NONE):
                    john.append(room)
                else:
                    john_branch.append(room)
            case _:
                print(f"{ERROR} Room {room} cannot be categorized by categorize_rooms_by_type() in categorize_rooms.py! {RESET}")
                room.print_stats()

    return normal, branch, entrance, john, entrance_branch, john_branch


