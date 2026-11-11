#Author: Stack Man
#Date: 11/11/2026

#Helper classes to maintain a memory of failed SD pairs
#When a bridge between two doors is tried and fails, those door's type and dir are remembered
#so that we don't re-attempt to connect those types later
from objects import Door
from enums import PathTime
from level_objects import BaseRoomPath, BranchRoomPath, RoomPath
from colors import WARNING,RESET

class SDType():
    def __init__(self, door: Door):
        self.door_type = door.door_type
        self.door_dir = door.door_dir

    def __eq__(self, other):
        if (type(other) != SDType):
            raise NotImplementedError(f"__eq__ of SDType not implemented for type of {type(other)}")

        return self.door_type == other.door_type and self.door_dir == other.door_dir

    def __hash__(self):
        return hash((self.door_type, self.door_dir))


class SDSet():
    def __init__(self, A: Door, B: Door):
        self.A = SDType(A)
        self.B = SDType(B)

    def __eq__(self, other):
        if (type(other) != SDSet):
            raise NotImplementedError(f"__eq__ of SDSet not implemented for type of {type(other)}")

        return self.A == other.A and self.B == other.B

    def __hash__(self):
        return hash((self.A, self.B))

class MemorySet():
    def __init__(self):
        #maintain a hash set of invalid SD pairs so they aren't retried, this does NOT get copied between recursive calls
        #separate sets by path time as some invalid pairs may be valid for a different path time

        print(f"{WARNING}WARNING: MEMORY SET CHECK IS DISABLED{RESET}")

        self.TW : set[SDSet] = set() 
        self.PT : set[SDSet] = set()
        self.NPT : set[SDSet] = set()

    def add(self, A: BaseRoomPath, B: BaseRoomPath, path_time: PathTime):
        return
        if (path_time == PathTime.PIZZATIME):
            self.add_PT(A, B)
        elif (path_time == PathTime.NOTPIZZATIME):
            self.add_NPT(A, B)
        else:
            self.add_TW(A, B)

    def contains(self, A: BaseRoomPath, B: BaseRoomPath, path_time: PathTime):
        return False 
        if (path_time == PathTime.PIZZATIME):
            return self.contains_PT(A, B)
        elif (path_time == PathTime.NOTPIZZATIME):
            return self.contains_NPT(A, B)
        else:
            return self.contains_TW(A, B)

    def get_branch_set(self, A: BaseRoomPath, B: BaseRoomPath, path_time: PathTime):
        if (type(A) != BranchRoomPath or type(B) != BranchRoomPath):
            raise ValueError(f"get_branch_set called on non-branch room paths {A.room} and {B.room}")

        if (path_time == PathTime.PIZZATIME):
            return SDSet(A.pt.start_door, B.pt.exit_door)
        else:
            return SDSet(A.npt.start_door, B.npt.exit_door)

    def get_TW_set(self, A: BaseRoomPath, B: BaseRoomPath):
        start_door = self.get_door(A)
        exit_door = self.get_door(B)

        return SDSet(start_door, exit_door)
    
    def add_PT(self, A: BaseRoomPath, B: BaseRoomPath):
        AB_set = self.get_branch_set(A, B, PathTime.PIZZATIME)
        self.PT.add(AB_set)

    def contains_PT(self, A: BaseRoomPath, B: BaseRoomPath):
        AB_set = self.get_branch_set(A, B, PathTime.PIZZATIME)
        return AB_set in self.PT

    def add_NPT(self, A: BaseRoomPath, B: BaseRoomPath):
        AB_set = self.get_branch_set(A, B, PathTime.NOTPIZZATIME)
        self.NPT.add(AB_set)

    def contains_NPT(self, A: BaseRoomPath, B: BaseRoomPath):
        AB_set = self.get_branch_set(A, B, PathTime.NOTPIZZATIME)
        return AB_set in self.NPT

    def add_TW(self, A: BaseRoomPath, B: BaseRoomPath):
        AB_set = self.get_TW_set(A, B)
        self.TW.add(AB_set)

    def contains_TW(self, A: BaseRoomPath, B: BaseRoomPath):
        AB_set = self.get_TW_set(A, B)
        return AB_set in self.TW

    def get_door(self, A: BaseRoomPath):
        if (type(A) == BranchRoomPath):
            return A.branch_door
        elif (type(A) == RoomPath):
            return A.path.start_door

        raise ValueError(f"get_door called on BaseRoomPath {A.room}")