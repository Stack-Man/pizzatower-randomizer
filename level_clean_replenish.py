#Author: Stack Man
#Date: 11/12/2026

#clean up traversals in FG based on FG.depleted_edges
#update the traversal type based on the OG traversal type and the new state of the edge

from graph_create import FlowGraphHandler
from graph_objects import DoorNode, CombinedDoorNode, EdgeTraversal, PathEdge
from graph_impossible_booking import store_edges_to_update_in_traversal, check_bipartites_for_traversal_type, update_all_in_bipartite_graph_no_type_check

from level_objects import TwowaySegment, BranchSegment, RoomSelection

import logging as log

from colors import CONTINUE, RESET

def all_traversals(FG: FlowGraphHandler):
    for N in FG.nodes():
        N: DoorNode|CombinedDoorNode
        for D, traversals in N.steps.items():
            for t in traversals:
                yield t, N, D

#Edges must update if their status would effect any bipartite graph
#This occurs when nodes are added or removed (NDB to 0 or away from 0)
#Or when the number of edges from an E node changes (NDB is 0 AND DB changes)
def store_traversal_updated_edges_batch(FG: FlowGraphHandler, updated_edges: set[PathEdge]):

    #dict to store to update traversals and its list of updated edges
    to_update : dict[EdgeTraversal, set[PathEdge]]= {} 

    #find all updated edges in a traversal and store them
    #for traversal, _, _ in all_traversals(FG):
        #for edge in updated_edges:
            #if edge in traversal:
                #add or append edge to traversal list
                #to_update.setdefault(traversal, set()).add(edge)
    
    for edge in updated_edges:
        traversal_containing_edge = FG.get_traversals_with_edge(edge)

        for traversal in traversal_containing_edge:
            to_update.setdefault(traversal, set()).add(edge)

    #for each traversal and its list of effected edges
    for traversal, edges in to_update.items():

        #update the traversal's bipartites with all of the effected edges, one by one
        store_edges_to_update_in_traversal(traversal, edges)

        #DONT perform these until we actually want to access the traversal later
        #perform impossible booking check only after we've completed updated all edges
        #new_traversal_type = check_bipartites_for_traversal_type(traversal.bipartiteTW, traversal.bipartitePT, traversal.bipartiteNPT)

        #set the new traversal type
        #traversal.traversal_type = new_traversal_type

def update_traversal_type(traversal: EdgeTraversal):
    #Update traversal's BGs with updated edges
    update_all_in_bipartite_graph_no_type_check(traversal, traversal.to_update)
    traversal.to_update.clear()
    
    #perform matching check after we've updated all edges
    new_traversal_type = check_bipartites_for_traversal_type(traversal.bipartiteTW, traversal.bipartitePT, traversal.bipartiteNPT)

    #set the new traversal type
    traversal.traversal_type = new_traversal_type

def get_selections(segment: TwowaySegment | BranchSegment):
    selections: list[RoomSelection] = []

    if (type(segment) == TwowaySegment):
        selections.append(segment.between_rooms)

        if (segment.has_loop_path):
            self_loop: RoomSelection = segment.loop_path         
            selections.append(self_loop)

    elif (type(segment) == BranchSegment):

        #NPT is cleaned before PT during bridge_branch
        #will get recleaned after TRY but we keep this here
        #so we can replenish after a DUMP
        selections.append(segment.npt_between_rooms)
        selections.append(segment.pt_between_rooms)

    else:
        raise NotImplementedError(f"get_selections not implemented for type {type(segment)}")

    return selections

# Clean:
# 1. for each room of each path in segment traversal
# 1b. remove that room's paths from FG
# 2. use bipartite graph to recalculate traversal type of traversals with removed paths

def clean_segment(FG: FlowGraphHandler, segment: TwowaySegment | BranchSegment):
    selections: list[RoomSelection] = get_selections(segment)
    clean_selections(FG, selections)
    
def clean_selections(FG: FlowGraphHandler, selections: list[RoomSelection]):
    #any edge whos NDB or DB paths were emptied
    depleted_edges: set[PathEdge] = set()

    #clean up all selections of the segment
    #and store unique depleted edges
    for selection in selections:
        #log.debug("About to clean selection")
        new_depleted_edges = clean_selection(selection)
        #log.debug("Cleaned selection")
        for e in new_depleted_edges:
            depleted_edges.add(e)
        #log.debug("stored depleted edges")

    #log.debug("About to store edges")

    #remove depleted edges from bipartite graphs of traversals containing them
    store_traversal_updated_edges_batch(FG, depleted_edges)

    #log.debug("stored edges")
    
def clean_selection(selection: RoomSelection):

    #store depleted edges so we can clean up traversals
    #set so each edge is only stored once
    to_update : set[PathEdge] = set() 

    for rp in selection.rooms:
        for path in rp.room.paths:
            edge : PathEdge = path.edge
            should_update = edge.remove(path)

            if (should_update):
                to_update.add(edge)

    return to_update

# Replenish:
# 1. for each room of each path in segment traversal 
# 1b. readd that room's paths to FG
# 2. use bipartite graph to recalculate traversal type of traversals with added paths
def replenish_segment(FG: FlowGraphHandler, segment: TwowaySegment | BranchSegment):
    selections: list[RoomSelection] = get_selections(segment)
    replenish_selections(FG, selections)

def replenish_selections(FG: FlowGraphHandler, selections: list[RoomSelection]):
    #any edge whose NDB or DB paths were moved from empty to not
    replenished_edges: set[PathEdge] = set()

    #clean up all selections of the segment
    #and store unique depleted edges
    for selection in selections:
        new_replenished_edges = replenish_selection(selection)

        for e in new_replenished_edges:
            replenished_edges.add(e)

    #update replenished edges 
    store_traversal_updated_edges_batch(FG, replenished_edges)

def replenish_selection(selection: RoomSelection):
    to_update : set[PathEdge] = set() 
    
    for rp in selection.rooms:
        for path in rp.room.paths:
            edge : PathEdge = path.edge
            should_update = edge.add(path)

            if (should_update):
                to_update.add(edge)

    return to_update
    