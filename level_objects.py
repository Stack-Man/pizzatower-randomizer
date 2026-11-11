#Author: Stack Man
#Date: 11/9/2026

from enums import RoomType
from objects import Room, Path, Door

class BaseRoomPath():
    def __init__(self, room: Room):
        self.room = room

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
    def __init__(self, rooms: list[BaseRoomPath]):
        self.rooms = rooms

class LevelSegment():
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath):
        self.start_room = start_room
        self.end_room = end_room
        self.is_john = end_room.room.room_type == RoomType.JOHN

class TwowaySegment(LevelSegment):
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath, between_rooms: RoomSelection):
        super().__init__(start_room, end_room)
        self.between_rooms = between_rooms

class BranchSegment(LevelSegment):
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath, pt_between_rooms: RoomSelection, npt_between_rooms: RoomSelection):
        super().__init__(start_room, end_room)
        self.pt_between_rooms = pt_between_rooms
        self.npt_between_rooms = npt_between_rooms

class Level():
    def __init__(self, segments: list[LevelSegment]):
        self.segments = segments