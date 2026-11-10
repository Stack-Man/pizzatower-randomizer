#Author: Stack Man
#Date: 11/9/2026

from objects import Room

class RoomSelection():
    def __init__(self, rooms: list[Room]):
        self.rooms = rooms

    def first_room(self):
        return self.rooms[0]

    def last_room(self):
        return self.rooms[len(self.rooms) - 1]

class LevelSegment():
    def __init__(self, start_room: Room, end_room: Room, is_john = False):
        self.start_room = start_room
        self.end_room = end_room
        self.is_john = is_john

class TwowaySegment(LevelSegment):
    def __init__(self, start_room: Room, end_room: Room, between_rooms: RoomSelection, is_john = False):
        super().__init__(start_room, end_room, is_john)
        self.between_rooms = between_rooms

class BranchSegment(LevelSegment):
    def __init__(self, start_room: Room, end_room: Room, pt_between_rooms: RoomSelection, npt_between_rooms: RoomSelection, is_john = False):
        super().__init__(start_room, end_room, is_john)
        self.pt_between_rooms = pt_between_rooms
        self.npt_between_rooms = npt_between_rooms

class Level():
    def __init__(self, segments: list[LevelSegment]):
        self.segments = segments