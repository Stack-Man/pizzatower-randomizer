#Author: Stack Man
#Date: 11/17/2025

import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
import random

from json_to_objects import json_to_rooms
from layer_creation import rooms_to_layers
from node_id_objects import NodeType, StartExitType
import node_id_objects as nio
from path_mapping import layer_to_paths_and_endpoints
from path_traversal import flow, find_path, grow_path
from path_objects import Endpoint, RoomPath

from enums import *

LAYER_PATH = "path"
LAYER_DOOR = "door"
LAYER_ROOM = "room"
LAYER_TRANSITION = "transition"
LAYER_TYPE = "type"

def hub_layout(G, hubs, transitions):
    pos = {}
    
    #TODO: better layout for the three columns of transition types
    
    #place hubs (rooms) equally spaced on two vertical lines
    
    #for each hub, place its doors clumped together on the line next to it
    
    #for each transition, place it equally spaced on a central line
    
    #=========================================
    #Sort transitions by type
    #=========================================
    i_ts = []
    s_ts = []
    e_ts = []
    
    for t_node in transitions:
        se_type = t_node.inner_id.start_exit_type
        
        if se_type == StartExitType.INITIAL:
            i_ts.append(t_node)
        elif se_type == StartExitType.START:
            s_ts.append(t_node)
        else:
            e_ts.append(t_node)
    
    i_col = 0
    s_col = 1000
    e_col = 4000
    
    i_height = 0
    s_height = 0
    e_height = 0
    
    transition_step_height = 1500
    
    #=========================================
    #Place all transitions in three veritcal lines
    #=========================================
    for i, t in enumerate(i_ts):
        
        t_x = i_col
        t_y = i * transition_step_height
        pos[t] = [t_x, t_y]
        
        i_height = i_height + transition_step_height
    
    for i, t in enumerate(s_ts):
        
        t_x = s_col
        t_y = i * transition_step_height + 300
        pos[t] = [t_x, t_y]
        
        s_height = s_height + transition_step_height
    
    for i, t in enumerate(e_ts):
        
        t_x = e_col
        t_y = i * transition_step_height + 600
        pos[t] = [t_x, t_y]
        
        e_height = e_height + transition_step_height
    
    
    total_height = max(i_height, s_height, e_height)
    
    
    #hubs_per_column = len(hubs)/2
    hubs_per_column = len(hubs)
    
    if (hubs_per_column == 0):
        hubs_per_column = 1
    
    space_per_hub = total_height  / hubs_per_column
    
    hub_distance = 4000
    
    start_door_distance = 2000
    exit_door_distance = 3000
    
    #===========================================
    #Place all rooms (hubs) in one veritcal line
    #Space and divide equally
    #===========================================
    for i, h_node in enumerate(hubs):
        
        #print(f"Pos for: {str(h_node)}")
        
        #row = math.ceil(i / 2)
        row = i
        h_y = row * space_per_hub
        
        #col = 1 if i % 2 == 0 else -1
        col = 1
        h_x = hub_distance * col
        
        #pos[h_node] = (h_x, h_y)
        #pos[h_node] = (0, 0)
        
        doors = G.neighbors(h_node)
        list_doors = list(doors)
        door_count = len(list_doors)
        
        #==================================================
        #Place all doors in two vertical lines by door type
        #==================================================
        
        print(f"    doors count: {str(door_count)}")
        
        start_doors = []
        exit_doors = []
        
        for door in list_doors:
            
            #print(f"        doors to check: {str(door)}")
            
            if door.inner_id.start_exit_type == StartExitType.START:
                #print(f"        added start: {str(door)}")
                start_doors.append(door)
            else:
                #print(f"        added exit: {str(door)}")
                exit_doors.append(door)
        
        for i, d in enumerate(start_doors):
            #print(f"    Pos for: {str(d)}")
            
            d_x = start_door_distance * col
            d_y = h_y + i * (space_per_hub / len(start_doors)) - 300
            pos[d] = (d_x, d_y)
        
        for i, d in enumerate(exit_doors):
            #print(f"    Pos for: {str(d)}")
            
            d_x = exit_door_distance * col
            d_y = h_y + i * (space_per_hub / len(exit_doors)) - 600
            pos[d] = (d_x, d_y)
        
        """
        #=================================================
        #Place all doors in the space alloted for that hub
        #In a circle
        #=================================================
        
        
        d_x = door_distance * col
        d_y = h_y + random.random() * 50 + 200
        circ = nx.circular_layout(G.subgraph(list_doors), scale = door_count * 100, center = [d_x, d_y])
        pos.update(circ)
        """

    return pos 

def draw_layer(layer, name):
    transitions = []
    hubs = []
    nodelist = []
    
    for node in layer.nodes():

        if node.node_type == NodeType.TRANSITION:
            transitions.append(node)
        elif node.node_type == NodeType.ROOM:
            hubs.append(node)
        else:
            nodelist.append(node)
    
    pos = hub_layout(layer, hubs, transitions)
    
    for n in hubs:
        layer.remove_node(n)
    
    #nodelist.extend(hubs)
    nodelist.extend(transitions)
    
    nodes_without_pos = [n for n in layer.nodes if n not in pos]
    msg = "Nodes without positions: "
    
    for n in nodes_without_pos:
        msg += ", " + str(n) + "\n"
    
    print(msg)
        
    fig = plt.figure(figsize=(6, 5))

    nx.draw(layer, pos,
            with_labels=False, 
            node_color="lightblue", 
            node_size=500, 
            font_size=10, nodelist = nodelist)
            
    plt.title(name)

    fig.canvas.manager.set_window_title(layer.graph["name"])
    
    nx.draw_networkx_labels(
        layer,
        pos,
        font_color="red"   # <-- label color
    )
    
    plt.show(block=False)

def draw_tree(G):
    
    set1 = []
    
    for node in G.nodes():
        if node.start_exit_type == StartExitType.START:
            set1.append(node)
    
    #pos = nx.bipartite_layout(G , set1)
    #plt.figure(figsize=(8, 6))
    #nx.draw(G, pos, with_labels=True, node_size=5000, node_color="skyblue", font_size=10, font_weight="bold")
    
    for node in G.nodes:
        print(f"Node {node}:")
        
        for k, v in node.steps.items():
            print(f"    {k}: {v}")
    
    #plt.show(block=False)

def test_parse(filename):

    with open(filename, "r") as f:
        file = json.load(f)
        print("JSON data loaded successfully:")

        rooms = json_to_rooms(file)

        layers = rooms_to_layers(rooms)
        test_layer = None
        
        for layer in layers:
            print("layer " + str(layer.graph["name"]))
            
            if layer.graph["name"] == "Two Way":
                test_layer = layer
                break
            
            #draw_layer(layer, "Layer")
        
        print("======================== GETING PATHS, G")
        all_paths, G = layer_to_paths_and_endpoints(test_layer)
        print("======================== INITIAL FLOW")
        G = flow(G)
        
        draw_tree(G)


        A = get_endpoint(G, StartExitType.START, DoorType.HORIZONTAL, DoorDir.RIGHT)
        F = get_endpoint(G, StartExitType.EXIT, DoorType.BOX, DoorDir.UP)
        
        print("======================== INITIAL PATH")
        path = find_path(G, all_paths, A, F)
        print_path(path)
        
        
        print("======================= REMAINING paths: ")
        

        for node in G.nodes():
            msg = f"Node {node}:"
            
            for N in G.neighbors(node):
                msg2 = msg + f" > {str(N)}"
                
                for N2 in G.neighbors(N):
                    if N2 is not node:
                        msg3 = msg2 + f" > {str(N2)}"
                        
                        for N3 in G.neighbors(N2):
                            
                            if N3 is not N:
                                msg4 = msg3 + f" > {str(N3)}"
                                print(msg4)
        
        draw_tree(G)
        
        print("======================== GROW 1")
        new_path = grow_path(G, all_paths, path)
        print_path(new_path)
        print("======================== GROW 2")
        new_path2 = grow_path(G, all_paths, new_path)
        print_path(new_path2)
        
        
        
        #draw_tree(G)

        plt.show()
        
    return

def print_path(path):
    print("path: ")
    for S in path:
        print(f"    {str(S[0])} via {str(S[1])} > ")

def get_endpoint(G, start, type, dir):
    for N in G.nodes():
        if N.start_exit_type == start and N.door_type == type and N.door_dir == dir:
            return N
    
    return None

def print_steps(G):
    print("Steps: ")
    for node in G.nodes:
        print(f"    {node}:")
        
        for k, v in node.steps.items():
            print(f"        {k}: {v}")

def test_path_grow():
    
    G = nx.DiGraph()
    
    AN = nio.create_transition_node_id(StartExitType.START, "A", 1)
    BN = nio.create_transition_node_id(StartExitType.START, "B", 1)
    CN = nio.create_transition_node_id(StartExitType.START, "C", 1)
    DN = nio.create_transition_node_id(StartExitType.EXIT, "D", 2)
    EN = nio.create_transition_node_id(StartExitType.EXIT, "E", 2)
    FN = nio.create_transition_node_id(StartExitType.EXIT, "F", 2)
    
    A = Endpoint(AN)
    B = Endpoint(BN)
    C = Endpoint(CN)
    D = Endpoint(DN)
    E = Endpoint(EN)
    F = Endpoint(FN)
    
   
    G.add_edge(A, D)
    G.add_edge(D, B)
    G.add_edge(B, E)
    G.add_edge(E, C)
    G.add_edge(C, F)
    G.add_edge(F, A)
    G.add_edge(A, F)
    G.add_edge(A, E)
    G.add_edge(A, B) #if we add AB first, it should be prioritized over AD, just for testing, such a path shouldnt exist because its start-start
   
    
    #initial flow
    G = flow(G)
    
    #room paths
    R_AD = RoomPath("R_AD", "A", "D")
    R_DB = RoomPath("R_DB", "D", "B")
    R_BE = RoomPath("R_BE", "B", "E")
    R_EC = RoomPath("R_EC", "E", "C")
    R_CF = RoomPath("R_CF", "C", "F")
    R_FA = RoomPath("R_FA", "F", "A")
    R_AF = RoomPath("R_AF", "A", "F")
    R_AE = RoomPath("R_AE", "A", "E")
    R_AB = RoomPath("R_AB", "A", "B")
    
    #construct paths in all_paths
    all_paths = {}
    all_paths[(A, D)] = [R_AD]
    all_paths[(D, B)] = [R_DB]
    all_paths[(B, E)] = [R_BE]
    all_paths[(E, C)] = [R_EC]
    all_paths[(C, F)] = [R_CF]
    all_paths[(F, A)] = [R_FA]
    all_paths[(A, F)] = [R_AF]
    all_paths[(A, E)] = [R_AE]
    all_paths[(A, B)] = [R_AB]
    
    print("======================== INITIAL")
    path = find_path(G, all_paths, A, E)
    print_path(path)
    #print_steps(G)
    
    print("======================== GROW 1")
    new_path, inc = grow_path(G, all_paths, path)
    print_path(new_path)
    #print_steps(G)
    
    print("======================== GROW 2")
    new_path2, inc2 = grow_path(G, all_paths, new_path)
    print_path(new_path2)
    #print_steps(G)
    

#test_parse("datafiles/json/johngutter.json")
test_path_grow()