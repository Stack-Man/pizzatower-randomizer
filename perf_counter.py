#Author: Stack Man
#Date: 11/16/2026

#Record performance times for different parts of the system, then report back

from enum import Enum
import time 


class PerfType(Enum):
    GEN = 0
    SEG = 1
    BRIDGE = 2
    ROOMPATH = 3
    TRAVERSAL = 4
    SELECTION = 5
    CLEAN = 6

start_times: dict[PerfType, float] = {}
total_times: dict[PerfType, float] = {}


def start_perf(type: PerfType):
    if (type in start_times):
        raise LookupError(f"PERF: {type} was not removed before next call!" )
    
    start_times[type] = time.perf_counter()

def end_perf(type: PerfType):
    prev_time = 0

    if (type in total_times):
        prev_time = total_times[type]

    new_time = time.perf_counter() - start_times[type]
    start_times.pop(type) #remove type so we ensure we never call end more than start

    total_times[type] = prev_time + new_time

def print_perf():

    for type in PerfType:
        if type in total_times:
            print(f"{type}: {total_times[type]}")