#Author: Stack Man
#Date: 11/13/2026

#Generate a single level segment of a specific type

from json_source_destination import SourceDestinationHandler
from graph_create import FlowGraphHandler

from level_objects import BranchRoomPath, BaseRoomPath, SelfLoopRoomPath, TwowaySegment

from enums import BranchType, TraversalType

from level_bridge import bridge_twoway_room_room, bridge_branch_room_room, bridge_branch_rp_room, bridge_twoway_rp_room, bridge_self_loop, bridge_oneway_room_room

from colors import ERROR, RESET, CAUTION, WARNING

from json_objects import Room

import logging as log


def entrance_or_entrance_branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler, failed_pairs: set[tuple[Room, Room]]):
    #Pick either E or EB
    for E_or_EB in SD.entrances():

        #if EB, create a Branch Segment with EB and some BE
        D_generator = SD.branch_ends
        bridge_generator = bridge_branch_room_room

        #if E, create a TwowaySegment with E and some BS
        if (E_or_EB.branch_type == BranchType.NONE):
            D_generator = SD.branch_starts
            bridge_generator = bridge_twoway_room_room

        for B in D_generator():

            #skip pairs that already failed completely
            if ((E_or_EB, B) in failed_pairs):
                continue
            
            for seg in bridge_generator(E_or_EB, B, FG):
                yield seg

            #if all segs were yielded, then this pair failed but is not consumed
            #we should add it to failed_pairs
            failed_pairs.add((E_or_EB, B))

    raise RuntimeError(f"{WARNING}Failed to generate any E or EB segment after entrances{RESET}")

def branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler, BS: BranchRoomPath):
    #create a BranchSegment with BS and some BE or JB
    for BA_or_BE in SD.branch_ends():
        for seg in bridge_branch_rp_room(BS, BA_or_BE, FG):
            yield seg

    raise RuntimeError(f"Failed to generate any branch segment from {BS.room} after attempts")

def john_branch_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler, BS_or_EB: BranchRoomPath):
    #create TwowaySegment with BS BA or EB  and some JB
    for JB in SD.john_branches():  
        for seg in bridge_branch_rp_room(BS_or_EB, JB, FG):
            return seg #return the first successful bridge
        
    raise RuntimeError(f"Failed to generate John Branch segment from {BS_or_EB.room} after JBs")

def john_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler, BE_or_E: BaseRoomPath):
    #create TwowaySegment with BE or E and some J
    for J in SD.just_johns():
        if (J.needs_self_loop): #special case for minigolf_8
            return john_segment_with_loop_rp(FG, BE_or_E, J)
        else:      
            for seg in bridge_twoway_rp_room(BE_or_E, J, FG):
                return seg #return the first successful bridge

    raise RuntimeError(f"Failed to generate any John segment from {BE_or_E.room}")

def john_segment_with_loop_rp(FG: FlowGraphHandler, BE_or_E: BaseRoomPath, J: Room):
    for seg in bridge_twoway_rp_room(BE_or_E, J, FG):
        try:
            return john_segment_with_loop(seg, BE_or_E.room, J, FG)
        except:
            pass

    raise RuntimeError(f"Failed to generate John segment from {BE_or_E.room} with loop")

def john_segment_with_loop_room(FG: FlowGraphHandler, E: Room, J: Room):
    for seg in bridge_twoway_room_room(E, J, FG):
        try:
            return john_segment_with_loop(seg, E, J, FG)
        except:
            pass

    raise RuntimeError(f"Failed to generate John segment from {E} with loop")

def john_segment_with_loop(seg: TwowaySegment, E_or_BE: Room, J: Room, FG: FlowGraphHandler):
    try:
        loop_path = bridge_self_loop(J, FG)
        seg.has_loop_path = True
        seg.loop_path = loop_path

        self_loop_room = SelfLoopRoomPath(J, J.self_loop.start, J.self_loop.end)
        seg.loop_room = self_loop_room

        return seg #return the first successful bridge  
    except:
        pass #failed to bridge with loop path
    
    raise RuntimeError(f"Failed to generate any John segment from {E_or_BE} with loop")

def between_branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler, BE: BaseRoomPath):
    #create TwowaySegment with Be and some BS or BA

    for BA_or_BS in SD.branch_starts():
        for seg in bridge_twoway_rp_room(BE, BA_or_BS, FG):
            yield seg

    raise RuntimeError(f"Failed to generate any between branch segment from {BE.room} after segments")

def ej_or_ejb_segment(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    #Create TwowaySegemnt between E and J or BranchSegment between EB and JB
    #Pick either E or EB
    try:
        for E_or_EB in SD.entrances():
            try: #inner try catch allows us to try with the next E instead of exiting immediately 

                #if E, create a TwowaySegment with E and some J
                if (E_or_EB.branch_type == BranchType.NONE):

                    for J in SD.just_johns(): 
                        #make sure we try all Js before terminating
                        try:
                            if (J.needs_self_loop):
                                return john_segment_with_loop_room(FG, E_or_EB, J)
                            else:
                                for seg in bridge_twoway_room_room(E_or_EB, J, FG):     
                                    return seg #return first valid seg
                        except:
                            pass

                    raise RuntimeError(f"No J to match E {E_or_EB}")
                
                #if EB, create a Branch Segment with EB and some JB
                else:
                    for JB in SD.john_branches():

                        #make sure we try all JBs before terminating
                        try:
                            for seg in bridge_branch_room_room(E_or_EB, JB, FG):
                                return seg
                        except:
                            pass

            except:
                
                pass
            
    except RuntimeError as e:
        pass

    raise RuntimeError(f"Failed to generate any EJ or EJB segment")

def ej_or_ejb_segment_forced(FG: FlowGraphHandler, SD: SourceDestinationHandler, E_name: str, J_name: str):
    E = SD.get_from_E_or_EB(E_name)
    J = SD.get_from_J_or_JB(J_name)

    if (E.branch_type == BranchType.NONE):
        for seg in bridge_twoway_room_room(E, J, FG):
            return seg
    else:
        for seg in bridge_branch_room_room(E, J, FG):
            return seg

    raise RuntimeError(f"No valid level between {E_name} and {J_name}")

def oneway_segment(FG: FlowGraphHandler, S: Room, E: Room, traversal_type: TraversalType):
    return bridge_oneway_room_room(S, E, traversal_type, FG)