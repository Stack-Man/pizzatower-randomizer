#Author: Stack Man
#Date: 11/17/2025

import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
import random

from object_creation import json_to_rooms
from layer_creation import rooms_to_layers
from node_id_objects import NodeType, StartExitType

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
    
    transition_step_height = 1000
    
    total_height = 0
    
    #=========================================
    #Place all transitions in a veritcal line
    #=========================================
    yi = 0
    ys = 0
    ye = 0
    
    for i, t_node in enumerate(transitions):
        
        x = 0
        
        se_type = t_node.inner_id.start_exit_type
        
        y = 0
        
        if  se_type == StartExitType.INITIAL:
            x = 0
            yi = yi + 1
            
            y = yi * transition_step_height
        elif se_type == StartExitType.START:
            x = 1000
            ys = ys + 1 + 200
            
            y = ys * transition_step_height
        else:
            x = 2000
            ye = ye + 1 + 100
            
            y = ye * transition_step_height
        
        t_x = x
        t_y = y
        
        pos[t_node] = [t_x, t_y]
        total_height = total_height + transition_step_height
    
    hubs_per_column = len(hubs)/2
    
    if (hubs_per_column == 0):
        hubs_per_column = 1
    
    space_per_hub = total_height  / hubs_per_column
    
    hub_distance = 4000
    
    door_distance = hub_distance / 2
    
    #===========================================
    #Place all rooms (hubs) in two veritcal line
    #Space and divide equally
    #===========================================
    for i, h_node in enumerate(hubs):
        
        #row = math.ceil(i / 2)
        row = i
        h_y = row * space_per_hub
        
        #col = 1 if i % 2 == 0 else -1
        col = 1
        h_x = hub_distance * col
        
        pos[h_node] = (h_x, h_y)
        
        doors = G.neighbors(h_node)
        list_doors = list(doors)
        door_count = len(list_doors)
        
        #=================================================
        #Place all doors in the space alloted for that hub
        #In a circle
        #=================================================
        
        d_x = door_distance * col
        d_y = h_y + random.random() * 50 + 200
        circ = nx.circular_layout(G.subgraph(list_doors), scale = door_count * 100, center = [d_x, d_y])
        pos.update(circ)

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

        """
        layer_type = layer.nodes[node].get(LAYER_TYPE)

        if layer_type == LAYER_TRANSITION:
            transitions.append(node)
        elif layer_type == LAYER_ROOM:
            hubs.append(node)
        else:
            nodelist.append(node)"""
    
    pos = hub_layout(layer, hubs, transitions)
    
    nodelist.extend(hubs)
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

def test_parse(filename):

    with open(filename, "r") as f:
        file = json.load(f)
        print("JSON data loaded successfully:")

        rooms = json_to_rooms(file)

        layers = rooms_to_layers(rooms)
        
        for layer in layers:
            print("drawing layer " + str(layer.graph["name"]))
            draw_layer(layer, "Layer")

        plt.show()
        
    return
    
test_parse("datafiles/json/johngutter.json")