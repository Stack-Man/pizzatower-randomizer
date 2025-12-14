#Author: Stack Man
#Date: 11/17/2025

import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math

from object_creation import json_to_rooms
from layer_creation import rooms_to_layers

LAYER_PATH = "path"
LAYER_DOOR = "door"
LAYER_ROOM = "room"
LAYER_TRANSITION = "transition"
LAYER_TYPE = "type"

def hub_layout(G, hubs, transitions):
    pos = {}
    
    #place hubs equally spaced on two vertical lines
    
    #for each hub, place its doors clumped together on the line next to it
    
    #for each transition, place it equally spaced on a central line
    
    transition_step_height = 1000
    
    total_height = 0
    
    #=========================================
    #Place all transitions in a veritcal line
    #=========================================
    for i, t_node in enumerate(transitions):
        t_x = 0
        t_y = i * transition_step_height
        
        pos[t_node] = [t_x, t_y]
        total_height = total_height + transition_step_height
    
    hubs_per_column = len(hubs)/2
    
    if (hubs_per_column == 0):
        hubs_per_column = 1
    
    space_per_hub = total_height  / hubs_per_column
    
    hub_distance = 2000
    
    door_distance = hub_distance / 2
    
    #===========================================
    #Place all rooms (hubs) in two veritcal line
    #Space and divide equally
    #===========================================
    for i, h_node in enumerate(hubs):
        
        row = math.ceil(i / 2)
        h_y = row * space_per_hub
        
        col = 1 if i % 2 == 0 else -1
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
        circ = nx.circular_layout(G.subgraph(list_doors), scale = door_count * 100, center = [d_x, h_y])
        pos.update(circ)

    return pos 

def draw_layer(layer, name):
    transitions = []
    hubs = []
    nodelist = []
    
    for node in layer.nodes():

        layer_type = layer.nodes[node].get(LAYER_TYPE)

        if layer_type == LAYER_TRANSITION:
            transitions.append(node)
        elif layer_type == LAYER_ROOM:
            hubs.append(node)
        else:
            nodelist.append(node)
    
    pos = hub_layout(layer, hubs, transitions)
    
    nodelist.extend(hubs)
    nodelist.extend(transitions)
        
    fig = plt.figure(figsize=(6, 5))

    nx.draw(layer, pos,
            with_labels=True, 
            node_color="lightblue", 
            node_size=500, 
            font_size=10, nodelist = nodelist)
            
    plt.title(name)

    fig.canvas.manager.set_window_title(layer.graph["name"])
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