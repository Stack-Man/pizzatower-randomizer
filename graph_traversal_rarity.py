#Author: Stack Man
#Date: 11/2/2026

#The rarity of a traversal is some factor of its length and the path rarity of each edge
#Separate rarities should be calculated for TW, PT, and NPT


#dont want to always use the most common for the same pair, it may get repetitive
#identify SD combo with the most rare set of choics, then choose for that combo first?
#should we allow other SD combos to choose first?

#all we need to do is prevent complete starvation...

#the exhaustive paths from the flow repersent all valid non-redundant paths between two SD combos
#if a path selection consumes an edge, we dont need to reflow, we only need
#to remoev all other paths containing taht edge

#though maybe we need to do something to account for double booking
#to account for when a room consumed puts some other generation in an impossible booking

#Suppose a path selection consumes an edge. 
# The initial flow contained all non-redundant paths between SD
# The new flow contains the same non-redundant paths, except those that contain the consumed edge
# Therefore, remove all paths from each SD that contain the consumed edge and we will have the new set of edges.

#Additionally, a consumed room may put a path into an impossible-booking
# The consumed room must have contained the last non DB path on an edge and that edge must not have been consumed
# For any paths containing that edge, add that edge to the bipartite graphs stored for each traversal and check for an impossible booking
# So for every path of every room that was consumed, get path type
# for every unqiue path type that was removed, check if that path was the last non DB of the edge and the edge still ahs DB paths
# for those edges, check for an impossible booking in the bipartite graph of any traversal containing that edge,
# add the new DB edge to the graph then check for an impossible booking

#TODO:
#use the same bipartite graph theory for SD combos and flow graph generations
#this will allow us to observe whether there is an impossible booking
#we will also have to modify it to detect whether double-bookable consumed rooms will make the booking impossible and how to satisfy

#the heory doesnt 100% work because a traversal can be used more than once... maybe have a node for every possible variation?
#but also the traversal are sometimes exclusiev withe ach other...

#so bipartite graph matching wont actually work well nvm

#We can immediatel assign any direct SD combos, they have no effect on the other SDs

#what limits each assignment is not the whole traversal, but the edegs within, speficialyl the lowest count edge
#each assignment reducest the count of every edge within by 1, possibly lowering the lowest count edge of other traversals
#some assignments may be with double booked rooms, reducing the edge count of multiple edges from one assignment, but whether
#an ssignment influences edges not within it depends onw hether a double booked room is consumed for the assignment

#so every SD combo is a node
#every traversal is a node
#connecting traversal to SDs is through a node with a weight
#that node reps an edge and the weigth is the amount of edges it can supply
#taht edge is the lowest count edge for that traversal

#though sometimes the lowest coutn edge can cahnge based on influence from other traversals...

#To summarize:
#Every SD has a set of valid traversals T
#Every T has a set of paths P
#Every P has a weight W

#Every SD needs one match T
#Matching of T decreases W for every P in T
#For any T with P where W == 0, T is invalid

#Find a SD to T matching where all SDs have a matching valid T

#T has a set of double-bookable paths DB
#Every DB has a set of paths P
#T has some room selection R
#R has a set of DB
#Matching of T with room selection R will decrease W for every P in DB for every DB in R and T

#Some clusters of T are strongly linked.
#For any pair of T, they are strongly linked if they both contain the same edge

#Some clusters of T are weakly linked
#For any pair of T, they are weakly linked if one contains a DBP that is an edge in the other

#GOAL:
#Find some matching of T with room selection R where no P in T < 0
#P < 0 indicates that there was overdraw, P = 0 indicates just enough to satisfy

#For any set of T that do not conflict with each other,
#Counte ach time a path P appears in any T
#All counts of P <= P.W, if not, there must be an invalidity

#TODO: how to find non conflicting T sets quickly, without trial and error?
#flaw: non-conflicting T sets do not consider which source-destination combinations are actually needed...
#we need ONE non-conflicting T set that matches our SDs
#rather than every non-conflicting T set that also assumes that every single T
#used within must be usable

#maybe we can say taht for any non-conflicting T set, any subset must also not conflict? that could help, but depends

#also possibly many types of non-conflicting T sets with slight variations, like ABCD vs ABCE

#maybe instead we find mutually exclusive T sets and know that we cant choose all of them?
#kind of hard, if it were only exclusion beween two its fine but if its only bad once the entire set exists, thats harder

#Once we have all non conflicting T sets, we can perform another check for impossible bookings
#The logic is the same as impossible bookings within a single traversal
#Every DB room could possible be assigned to one of many traversals in the set
#we find combinations that avoid impossible bookings or cant be impossibly booked due to saturation of non DB opaths regardless of DB choices

#1. remove all T that do not match any SD
#2. for each SD, list the T it can use

#re-use the flow graph idea to quickly iterate over all possible unqiue combinations?
# while cuonting paths to ensure C <= P.W
# would want to eliminate redundant re-orderings... though maybe its okay to process them anyways

#3. Find a non-conflicting T-set with at least one T from each group




from graph_objects import PathEdge

def get_traversal_rarity(edge: PathEdge):
    return 0