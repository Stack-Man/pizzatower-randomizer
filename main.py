#Author: Stack Man
#Date: 11/9/2026

#Run the program

#TODO: BS to JB can take awhile (0.7s - 1s)
#TODO: Try Immediate E to J can also take awhile
#TODO: replace tower_tutorial1N/tower_tutorial with custom option between the two
#and use it for both peppino and noise

#TODO: random seed is not deterministic anymore.
#initial level structure is not consistent

#might be caused by some iteration over dicts (such as get_traversal), nah not that bc that's just a list

#TODO: can we optimize get_traversals_between to not iterate over all nodes looking for the combined node that contains N?
#and for the K taht contains D, this combinedDoorNode may improve flow performance but afterwards it's not good
#maybe we can use an index tleling us which node contains our simpel door noed so we dont have to search each time