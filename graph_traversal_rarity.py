#Author: Stack Man
#Date: 11/2/2026

#The rarity of a traversal is some factor of its length and the path rarity of each edge
#Separate rarities should be calculated for TW, PT, and NPT


from graph_objects import PathEdge

def get_traversal_rarity(edge: PathEdge):
    return 0