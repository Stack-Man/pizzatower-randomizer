#Author: Stack Man
#Date: 11/17/2025

from parse import read_json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math

def hub_layout(G, hubs, transitions):
    pos = {}
    print(str(hubs))
    
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
        
        pos[str(t_node)] = (t_x, t_y)
        
        print(str(t_node) + " at " + str(t_x) + ", " + str(t_y))
        
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
        
        #print(str(h_x) + "=" + str(hub_distance) + "*" + str(col))
        
        #pos[h_node] = (h_x, h_y)
        
        print(str(h_node) + " at " + str(h_x) + ", " + str(h_y))
        
        doors = G.neighbors(str(h_node))
        list_doors = list(doors)
        door_count = len(list_doors)
        
        #=================================================
        #Place all doors in the space alloted for that hub
        #In a circle
        #=================================================
        
        circ = nx.circular_layout(G.subgraph(list_doors), center = (col, h_y))
        print(circ)
        pos.update(circ)
        
        
        """
        for k, d_node in enumerate(G.neighbors(str(h_node))):
            
            d_x = col * door_distance
            d_y = h_y + k * space_per_door
            
            pos[str(d_node)] = (d_x, d_y)
            
            #print(str(d_node) + " at " + str(d_x) + ", " + str(d_y))
        """
    
    #remoe room nodes so that theyre not included in the visualization
    G.remove_nodes_from(hubs)

    return G, pos 

def test_parse(filename):
    G = read_json(filename)

    door_endings = ["_A", "_B", "_C", "_D", "_E", "_F", "_G"]
    transition_words = ["door", "box", "horizontal", "vertical", "rocket", "taxi"]
    
    node_sizes = []
    transitions = []
    hubs = []
    
    large_node = 500
    small_node = 100
    
    for node in G.nodes():
        
        if any(sub in str(node) for sub in transition_words):
            transitions.append(node)
            node_sizes.append(large_node)
        elif not any(sub in str(node) for sub in door_endings):
            hubs.append(node)
            node_sizes.append(large_node)
        else:
            node_sizes.append(small_node)
    

    G, pos = hub_layout(G, hubs, transitions)
    nx.draw(G, pos,
        with_labels=True, 
        node_color="lightblue", 
        node_size=node_sizes, 
        font_size=10)
    
    #edge_labels = {}
    #for u, v, data in G.edges(data=True):
        #if 'time' in data:
            #edge_labels[(u, v)] = f"T:{data['time']}\nD:{data['dir']}"
        
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    
    plt.title(f"{filename} graph")
    plt.show()
    
test_parse("datafiles/json/johngutter.json")