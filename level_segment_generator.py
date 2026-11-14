#Author: Stack Man
#Date: 11/13/2026

#Generate a single level segment of a specific type

from json_source_destination import SourceDestinationHandler
from graph_from_rooms import FlowGraphHandler

from level_objects import BranchRoomPath, BaseRoomPath

from enums import BranchType

from level_bridge import bridge_twoway_room_room, bridge_branch_room_room, bridge_branch_rp_room, bridge_twoway_rp_room

LOG_FAILED_SEGMENT_GEN = True

def log_sg(msg: str|RuntimeError):
    if (LOG_FAILED_SEGMENT_GEN):
        print(msg, flush = True)

def entrance_or_entrance_branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    #Pick either E or EB
    for E_or_EB in SD.entrances():
        E_or_EB.print_stats()
        #if E, create a TwowaySegment with E and some BS
        if (E_or_EB.branch_type == BranchType.NONE):
            log_sg(f"entrance_or_entrance_branch_segments: {E_or_EB} was E")
            for BS_or_BA in SD.branch_starts(): 
                for seg in bridge_twoway_room_room(E_or_EB, BS_or_BA, FG):     
                    yield seg
        #if EB, create a Branch Segment with EB and some BE
        else:
            log_sg(f"entrance_or_entrance_branch_segments: {E_or_EB} was EB")
            for BE_or_BA in SD.branch_ends():
                for seg in bridge_branch_room_room(E_or_EB, BE_or_BA, FG):
                    yield seg

    raise RuntimeError(f"Failed to generate any E or EB segment")

def branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler, BS: BranchRoomPath):
    #create a BranchSegment with BS and some BE or JB
    for BA_or_BE in SD.branch_ends():
        for seg in bridge_branch_rp_room(BS, BA_or_BE, FG):
            yield seg

    raise RuntimeError(f"Failed to generate any branch segment from {BS.room}")

def john_branch_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler, BS_or_EB: BaseRoomPath):
    #create TwowaySegment with BE or E and some J
    for JB in SD.john_branches():
        for seg in bridge_twoway_rp_room(BS_or_EB, JB, FG):
            return seg #return the first successful bridge

    raise RuntimeError(f"Failed to generate John Branch segment from {BS_or_EB.room}")

def john_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler, BE_or_E: BaseRoomPath):
    #create TwowaySegment with BE or E and some J
    for J in SD.just_johns():
        for seg in bridge_twoway_rp_room(BE_or_E, J, FG):
            return seg #return the first successful bridge

    raise RuntimeError(f"Failed to generate any John segment from {BE_or_E.room}")

def between_branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler, BE: BaseRoomPath):
    #create TwowaySegment with Be and some BS or BA

    for BA_or_BS in SD.branch_starts():
        for seg in bridge_twoway_rp_room(BE, BA_or_BS, FG):
            yield seg

    raise RuntimeError(f"Failed to generate any between branch segment from {BE.room}")

def ej_or_ejb_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    #Create TwowaySegemnt between E and J or BranchSegment between EB and JB

    #Pick either E or EB
    try:
        for E_or_EB in SD.entrances():
            #if E, create a TwowaySegment with E and some J

            log_sg(f"ej_or_ejb_segment with {E_or_EB} of branch type {E_or_EB.branch_type}")

            if (E_or_EB.branch_type == BranchType.NONE):
                for J in SD.just_johns(): 
                    for seg in bridge_twoway_room_room(E_or_EB, J, FG):     
                        return seg #return first valid seg
                raise RuntimeError(f"No J to match E {E_or_EB}")
            #if EB, create a Branch Segment with EB and some JB
            else:
                for JB in SD.john_branches():
                    for seg in bridge_branch_room_room(E_or_EB, JB, FG):
                        return seg
                raise RuntimeError(f"No JB to match EB {E_or_EB}")
    except RuntimeError as e:
        log_sg(e)
    
    raise RuntimeError(f"Failed to generate any EJ or EJB segment")