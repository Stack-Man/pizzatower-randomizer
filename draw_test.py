import networkx as nx
from node_id_objects import StartExitType

import matplotlib.pyplot as plt
def draw_tree(G):
    
    set1 = []
    
    for node in G.nodes():
        if node.start_exit_type == StartExitType.START:
            set1.append(node)
    
    pos = nx.bipartite_layout(G , set1)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_size=5000, node_color="skyblue", font_size=5, font_weight="bold")
    
    """
    for node in G.nodes:
        print(f"Node {node}:")
        
        for k, v in node.steps.items():
            print(f"    {k}: {v}")"""
    
    plt.show(block=True)