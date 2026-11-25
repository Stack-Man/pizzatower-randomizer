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



def entrance_or_entrance_branch_segments(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    #Pick either E or EB
    for E_or_EB in SD.entrances():
        #E_or_EB.print_stats()
        #if E, create a TwowaySegment with E and some BS
        if (E_or_EB.branch_type == BranchType.NONE):
            #surround each bridge generator with try catch in case
            #bridge fails, we can continue with the next SD pair

            for BS_or_BA in SD.branch_starts(): 
                
                log.debug("Try with bridge with EB %s and %s",E_or_EB, BS_or_BA)  
                for seg in bridge_twoway_room_room(E_or_EB, BS_or_BA, FG):
                    
                    log.debug("Try with seg with EB %s and %s",E_or_EB, BS_or_BA)  
                    yield seg
            
        #if EB, create a Branch Segment with EB and some BE
        else:      
            for BE_or_BA in SD.branch_ends():
                log.debug("Try with bridge with E %s and %s", E_or_EB, BE_or_BA)  

                for seg in bridge_branch_room_room(E_or_EB, BE_or_BA, FG):
                    
                    log.debug("Try with seg with E %s and %s", E_or_EB, BE_or_BA)  
                    
                    yield seg
                

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

        log.debug("success gen loop_path with seg")
        return seg #return the first successful bridge  
    except:
        log.debug("failed to gen loop_path with seg")
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

            log.debug("Try %s immediate to J/JB", E_or_EB)
            
            try: #inner try catch allows us to try with the next E instead of exiting immediately 

                #if E, create a TwowaySegment with E and some J
                if (E_or_EB.branch_type == BranchType.NONE):

                    log.debug("Try %s immediate to J with %i Js", E_or_EB, len(SD.J))
                
                    for J in SD.just_johns(): 

                        log.debug("Try %s immediate to %s", E_or_EB, J)

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

                    log.debug("Try %s immediate to JB with %i JBs", E_or_EB, len(SD.JB))
                    
                    for JB in SD.john_branches():

                        log.debug("Try %s immediate to %s", E_or_EB, JB)

                        #make sure we try all JBs before terminating
                        try:
                            for seg in bridge_branch_room_room(E_or_EB, JB, FG):
                                return seg
                        except:
                            pass

                    log.debug(f"No JB to match EB {E_or_EB}")
                        
            except:
                
                pass
            
    except RuntimeError as e:
        pass

    raise RuntimeError(f"Failed to generate any EJ or EJB segment")

def oneway_segment(FG: FlowGraphHandler, S: Room, E: Room, traversal_type: TraversalType):
    return bridge_oneway_room_room(S, E, traversal_type, FG)