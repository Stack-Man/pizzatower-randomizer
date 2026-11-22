#Author: Stack Man
#Date: 11/12/2026

#clean up traversals in FG based on FG.depleted_edges
#update the traversal type based on the OG traversal type and the new state of the edge

from graph_create import FlowGraphHandler
from graph_objects import DoorNode, CombinedDoorNode, EdgeTraversal, PathEdge
from graph_impossible_booking import update_in_bipartite_graph

from level_objects import TwowaySegment, BranchSegment, RoomSelection

import logging as log

#TODO: we are only updating traversals of depleted or removed edges
#HOWEVER: every edge that has a room added/removed MUST be updated
#to preserve the state of the bipartite graph
#since the number of connections between edge node and room nodes changes every time a room is removed/added
#not just when the entire edge is depleted/replenished

#instead of updating every traversal based on edges,
#update every traversal that contains any removed edges
#upadte the bipartites with all edges all at once (just reconstruct?)
#and then find the traversal type at the end?
#(traversal type kind of relies on the per-edge traversal type to track NPT/PT stuff so maybe not)

#okay first, only DB rooms are in the bipartite, if any edge has a NDB room then it doesnt need to be part of the bipartite
#second, the number of DB rooms assigned to each E node DOES matter, since that effects assignment

#therefore, we only need to update traversals based on edges whose number of DB rooms changed, or whose number of NDB path went from 0 to 1 or vice versa

#SECOND: an invalidated traversalw ill stay invalid when updating with replenished edges, it doesn't understand that the invalidity is gone
#for this, design an algorithm that considers ALL edges at once to determine new type?
#but depleting and edge and making an impossible traversal does nota ctually mark it as invalid
#it has a zero edge but its not invalid (zero edges are still checked for)

#i believe that the traversal will remember its overall traversal type when depleted, what we need to know is if 
#an impossible booking can occur
#an impossible booking would mark its type as invalid, and it won't be reverted when replenished and no longer impossible...
#if an edge is depleted, that would by definition cause an impossible booking (connected component where E > R (E is 1 and R is 0))
#okay so yes we do need something to remember the previous traversal type or reconstruct it when adding
#since the type can change in multiple ways (like TW to OW only and then later to invalid) we will have to reconsider all edges again when we add

#in summary:
#1. update traversals with edges where (NDB = 0 & new_DB != old_DB) or (NDB 1 > 0 or NDB 0 > 1)
#2. modify bipartite update to consider updating an edge instead of adding a new one (must consider all edges to determine new type) (reconstruct?)

#reconstructing will be expensive, about as expensive as all those deepcopies... avoid it if possible

#if wwe modify the edges on each bipartite, regardless of whether they were possible or not, we can see again if they are possible
# the "use old type" method was simply a time saving method to avoid modifying already "impossible" graphs

def all_traversals(FG: FlowGraphHandler):
    for N in FG.nodes():
        N: DoorNode|CombinedDoorNode
        for D, traversals in N.steps.items():
            for t in traversals:
                yield t, N, D

#Edges must update if their status would effect any bipartite graph
#This occurs when nodes are added or removed (NDB to 0 or away from 0)
#Or when the number of edges from an E node changes (NDB is 0 AND DB changes)
def update_traversals(FG: FlowGraphHandler, updated_edges: set[PathEdge]):

    #TODO: batch modified traversals and don't check traversal type until all updated edges have been applied
    
    for edge in updated_edges:
        for traversal, _, _ in all_traversals(FG):
            if (edge in traversal):
                update_traversal_type(traversal, edge)

    return FG

def update_traversal_type(traversal: EdgeTraversal, edge: PathEdge):
    new_traversal_type = update_in_bipartite_graph(traversal.bipartiteTW, traversal.bipartitePT, traversal.bipartiteNPT, edge)
    old_traversal_type = traversal.traversal_type
    traversal.traversal_type = new_traversal_type

    #log.debug("Traversal %s from %s to %s", str(traversal), old_traversal_type, new_traversal_type)

    #if invalid, don't remove, keep the traversal, it'll just have an invalid type and won't be used

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
        new_depleted_edges = clean_selection(selection)

        for e in new_depleted_edges:
            depleted_edges.add(e)

    #remove depleted edges from bipartite graphs of traversals containing them
    update_traversals(FG, depleted_edges)
    
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
    update_traversals(FG, replenished_edges)

def replenish_selection(selection: RoomSelection):
    to_update : set[PathEdge] = set() 
    
    for rp in selection.rooms:
        for path in rp.room.paths:
            edge : PathEdge = path.edge
            should_update = edge.add(path)

            if (should_update):
                to_update.add(edge)

    return to_update
    