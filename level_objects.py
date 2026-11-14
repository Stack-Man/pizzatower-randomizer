#Author: Stack Man
#Date: 11/9/2026

from enums import RoomType
from objects import Room, Path, Door

class BaseRoomPath():
    def __init__(self, room: Room):
        self.room = room

    def __str__(self):
        return str(self.room)

class RoomPath(BaseRoomPath):
    def __init__(self, room: Room, path: Path):
        super().__init__(room)
        self.path = path

class BranchRoomPath(BaseRoomPath):
    def __init__(self, room: Room, npt: Path, pt: Path, branch_door: Door):
        super().__init__(room)
        self.npt = npt
        self.pt = pt
        self.branch_door = branch_door

class RoomSelection():
    def __init__(self, rooms: list[RoomPath]):
        self.rooms = rooms

    def __str__(self):
        msg = ""
        
        for RP in self.rooms:
            msg += RP.room.name + ": " + str(RP.path) + " > "

        return msg

class LevelSegment():
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath):
        self.start_room = start_room
        self.end_room = end_room
        self.is_john = end_room.room.room_type == RoomType.JOHN

    def __str__(self):
        msg = "Seg = S: " + str(self.start_room) + " > D: " + str(self.end_room)
        return msg

class TwowaySegment(LevelSegment):
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath, between_rooms: RoomSelection):
        super().__init__(start_room, end_room)
        self.between_rooms = between_rooms

    def __str__(self):
        msg = "TW Seg = S:" + str(self.start_room)

        for room in self.between_rooms.rooms:
            msg += " > " + str(room)

        msg += " > D: " + str(self.end_room)

        return msg

class BranchSegment(LevelSegment):
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath, pt_between_rooms: RoomSelection, npt_between_rooms: RoomSelection):
        super().__init__(start_room, end_room)
        self.pt_between_rooms = pt_between_rooms
        self.npt_between_rooms = npt_between_rooms

    def __str__(self):
        msg = "Branch Seg: \n"
        msg += "     NPT Seg = S:" + str(self.start_room)

        for room in self.npt_between_rooms.rooms:
            msg += " > " + str(room)

        msg += " > D: " + str(self.end_room)

        msg += "\n"

        msg += "     PT Seg = S:" + str(self.end_room)
        
        for room in self.pt_between_rooms.rooms:
            msg += " > " + str(room)

        msg += " > D: " + str(self.start_room)

        return msg

class Level():

    def __init__(self, segments: list[BranchSegment | TwowaySegment]):
        self.segments = segments
        self.name = segments[0].start_room.room.name

    def __str__(self):
        msg = ""

        for segment in self.segments:
            msg += str(segment) + "\n"

        return msg