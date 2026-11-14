#Author: Stack Man
#Date: 11/9/2026

#Categorize potential Source and Destination rooms
#Entrance, John, and Branch rooms

from objects import Room
from enums import RoomType, BranchType
from colors import WARNING, RESET
from level_objects import TwowaySegment, BranchSegment, LevelSegment

import random

class SourceDestinationHandler():
    def __init__ (self, E: list[Room], EB: list[Room], J: list[Room], JB: list[Room], BA: list[Room], BS: list[Room], BE: list[Room]):

        #TODO: use seeded randomization to randomize the order of rooms. This will be part of our randomization.

        self.E = E
        self.EB = EB
        self.J = J
        self.JB = JB
        self.BA = BA
        self.BS = BS
        self.BE = BE

    def remove_SD_in_segment(self, seg: LevelSegment):
        source = seg.start_room.room
        destination = seg.end_room.room

        self.remove_room_by_type(source)
        self.remove_room_by_type(destination)

    def remove_room_by_type(self, source: Room):
        match source.room_type:
            case RoomType.ENTRANCE:
                if (source.branch_type == BranchType.NONE):
                    self.remove_from(self.E, source)
                else:
                    self.remove_from(self.EB, source)
            case RoomType.JOHN:
                if (source.branch_type == BranchType.NONE):
                    self.remove_from(self.J, source)
                else:
                    self.remove_from(self.JB, source)
            case RoomType.BRANCH:
                match source.branch_type:
                    case BranchType.ANY:
                        self.remove_from(self.BA, source)
                    case BranchType.START:
                        self.remove_from(self.BS, source)
                    case BranchType.END:
                        self.remove_from(self.BE, source)
                    case _:
                        raise NotImplementedError(f"SourceDestinationHandler() remove not implemented for type {source.branch_type}")
        

    def remove_from(self, list: list[Room], room: Room):
        try:
            list.remove(room)
        except Exception:
            pass

    def entrance_count(self):
        return len(self.E) + len(self.EB)

    def entrances(self):
        return self.iterate_over([self.E, self.EB])

    def branch_starts(self):
        return self.iterate_over([self.BS, self.BA])

    def branch_ends(self):
        return self.iterate_over([self.BE, self.BA])

    def just_johns(self):
        return self.iterate_over([self.J])

    def john_branches(self):
        return self.iterate_over([self.JB])

    def iterate_over(self, lists):
        for L in lists:
            for l in L:
                yield l

    def copy(self):
        #only the lists themselves need to be unique
        #the Rooms within are just for reference
        return SourceDestinationHandler(self.E.copy(), self.EB.copy(), self.J.copy(), self.JB.copy(), self.BA.copy(), self.BS.copy(), self.BE.copy())


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
        if room.branch_type == BranchType.NONE:
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