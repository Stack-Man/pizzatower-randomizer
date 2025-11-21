#Author: Stack Man
#Date: 11/17/2025

from parse import read_json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math

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
        
        pos[str(t_node)] = [t_x, t_y]
        total_height = total_height + transition_step_height
    
    hubs_per_column = len(hubs)/2
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
        
        doors = G.neighbors(str(h_node))
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

def test_parse(filename):
    G = read_json(filename)

    door_endings = ["_A", "_B", "_C", "_D", "_E", "_F", "_G"]
    transition_words = ["door", "box", "horizontal", "vertical", "rocket", "taxi"]

    transitions = []
    hubs = []
    nodelist = []
    
    for node in G.nodes():
        
        if any(sub in str(node) for sub in transition_words):
            transitions.append(node)
        elif not any(sub in str(node) for sub in door_endings):
            hubs.append(node)
        else:
            nodelist.append(node)
    
    pos = hub_layout(G, hubs, transitions)
    
    G.remove_nodes_from(hubs)
    G.remove_nodes_from(transitions)
    
    nx.draw(G, pos,
        with_labels=True, 
        node_color="lightblue", 
        node_size=500, 
        font_size=10, nodelist = nodelist)
    
    plt.title(f"{filename} graph")
    plt.show()
    
test_parse("datafiles/json/johngutter.json")