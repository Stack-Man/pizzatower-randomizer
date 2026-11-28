#Author: Stack Man
#Date: 11/9/2026

from enums import RoomType
from json_objects import Room, Path, Door
from typing import Any

class BaseRoomPath():
    def __init__(self, room: Room):
        self.room = room

    def __str__(self):
        return str(self.room)

class SelfLoopRoomPath(BaseRoomPath):
    def __init__(self, room: Room, start: Path, end: Path):
        super().__init__(room)
        self.start = start
        self.end = end

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

    def __len__(self):
        return len(self.rooms)

class LevelSegment():
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath):
        self.start_room = start_room
        self.end_room = end_room
        self.is_john = end_room.room.room_type == RoomType.JOHN

    def __str__(self):
        msg = "Seg = S: " + str(self.start_room) + " > D: " + str(self.end_room)
        return msg

    def __len__(self):
        return 2

class TwowaySegment(LevelSegment):
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath, between_rooms: RoomSelection):
        super().__init__(start_room, end_room)
        self.between_rooms = between_rooms
        self.has_loop_path : bool = False
        self.loop_path : Any = None
        self.loop_room: Any = None

    def btw_rooms(self):
    
        #yield self.start_room

        for r in self.between_rooms.rooms:
            yield r

        #yield self.end_room

        if (self.has_loop_path):
            for r in self.loop_path.rooms:
                yield r

    def __str__(self):
        msg = "TW Seg = S:" + str(self.start_room)

        if (type(self.start_room) == BranchRoomPath):
            msg += " " + str(self.start_room.branch_door)
        elif(type(self.start_room) == RoomPath):
            msg += " " + str(self.start_room.path)

        for room in self.between_rooms.rooms:
            msg += " > " + str(room) + " " + str(room.path)

        msg += " > D: " + str(self.end_room)

        if (type(self.end_room) == BranchRoomPath):
            msg += " " + str(self.end_room.branch_door)
        elif(type(self.end_room) == RoomPath):
            msg += " " + str(self.end_room.path)

        if (self.has_loop_path):
            msg += f"\n     LOOP PATH: {self.loop_room.room} {self.loop_room.start.exit_door} > "
            msg += str(self.loop_path) + f"{self.loop_room.room} {self.loop_room.end.start_door}"

        return msg

    def __len__(self):
        return 2 + len(self.between_rooms)

class BranchSegment(LevelSegment):
    def __init__(self, start_room: BaseRoomPath, end_room: BaseRoomPath, pt_between_rooms: RoomSelection, npt_between_rooms: RoomSelection):
        super().__init__(start_room, end_room)
        self.pt_between_rooms = pt_between_rooms
        self.npt_between_rooms = npt_between_rooms

    def btw_rooms(self):

        #yield self.start_room

        for r in self.pt_between_rooms.rooms:
            yield r

        for r in self.npt_between_rooms.rooms:
            yield r

        #yield self.end_room

    def __str__(self):
        msg = "Branch Seg: \n"
        msg += "     NPT Seg = S:" + str(self.start_room)

        if (type(self.start_room) == BranchRoomPath):
            msg += " " + str(self.start_room.npt)
        elif(type(self.start_room) == RoomPath):
            msg += " " + str(self.start_room.path)

        for room in self.npt_between_rooms.rooms:
            msg += " > " + str(room) + " " + str(room.path)

        msg += " > D: " + str(self.end_room)

        if (type(self.end_room) == BranchRoomPath):
            msg += " " + str(self.end_room.npt)
        elif(type(self.end_room) == RoomPath):
            msg += " " + str(self.end_room.path)

        msg += "\n"

        msg += "     PT Seg = S:" + str(self.end_room)

        if (type(self.end_room) == BranchRoomPath):
            msg += " " + str(self.end_room.pt)
        elif(type(self.end_room) == RoomPath):
            msg += " " + str(self.end_room.path.start_door)
        
        for room in self.pt_between_rooms.rooms:
            msg += " > " + str(room) + " " + str(room.path)

        msg += " > D: " + str(self.start_room)

        if (type(self.start_room) == BranchRoomPath):
            msg += " " + str(self.start_room.pt)
        elif(type(self.start_room) == RoomPath):
            msg += " " + str(self.start_room.path)

        return msg

    def __len__(self):
        return 2 + len(self.npt_between_rooms) + len(self.pt_between_rooms)

class Level():

    def __init__(self, segments: list[BranchSegment | TwowaySegment]):
        self.segments = segments
        self.name = segments[0].start_room.room.name

    def __str__(self):
        msg = ""

        for segment in self.segments:
            msg += str(segment) + "\n"

        return msg

    def __len__(self):
        i = 0

        for seg in self.segments:
            i += len(seg)

        return i
