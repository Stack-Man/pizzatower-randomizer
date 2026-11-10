#Author: Stack Man
#Date: 11/9/2026

#Categorize potential Source and Destination rooms
#Entrance, John, and Branch rooms

from objects import Room
from enums import RoomType, BranchType
from colors import WARNING, RESET

import random

class SourceDestinationHandler():
    def __init__ (self, E: list[Room], EB: list[Room], J: list[Room], JB: list[Room], BA: list[Room], BS: list[Room], BE: list[Room]):
        self.E = E
        self.EB = EB
        self.J = J
        self.JB = JB
        self.BA = BA
        self.BS = BS
        self.BE = BE

    def entrance_count(self):
        return len(self.E) + len(self.EB)

    def get_entrance(self):
        return self.get_one_from_two(self.E, self.EB)

    def get_john_no_branch(self):
        return self.get_one_from_two(self.J, [])
    
    def get_branch_start(self):
        return self.get_one_from_two(self.BS, self.BA)

    def get_branch_end(self):
        return self.get_one_from_two(self.BE, self.BA)

    def get_john_branch_or_branch_end(self, force_john):
        if (force_john):
            return self.get_one_from_two(self.JB, [])
        else:
            return self.get_branch_end()

    def get_one_from_two(self, A, B):
        a_count = len(A)

        min = 0
        max = a_count + len(B)

        i = random.randrange(min, max)

        if (i > a_count):
            i -= a_count
            return A[i]

        return B[i]

def get_source_destination_rooms(rooms: list[Room]):

    entrance = []
    john = []
    branch = []

    for room in rooms:

        match room.room_type:
            case RoomType.ENTRANCE:
                entrance.append(room)
            case RoomType.JOHN:
                john.append(room)
            case RoomType.BRANCH:
                branch.append(room)

    E, EB = branch_from_EJ(entrance)
    J, JB = branch_from_EJ(john)

    BA, BS, BE = branch_by_type(branch)

    return SourceDestinationHandler(E, EB, J, JB, BA, BS, BE)

def branch_from_EJ(rooms: list[Room]):

    normal = []
    branch = []

    for room in rooms:
        if room.branch_type != BranchType.NONE:
            normal.append(room)
        else:
            branch.append(room)

    return normal, branch

def branch_by_type(rooms: list[Room]):
    branch_any = []
    branch_start = []
    branch_end = []

    print(f"{WARNING}WARNING: IGNORING BRANCH ROOMS OF TYPE MID, FORCEDSTART, FORCEDEND{RESET}")

    for room in rooms:

        match room.branch_type:
            case BranchType.ANY:
                branch_any.append(room)
            case BranchType.START:
                branch_start.append(room)
            case BranchType.END:
                branch_end.append(room)
            

    return branch_any, branch_start, branch_end