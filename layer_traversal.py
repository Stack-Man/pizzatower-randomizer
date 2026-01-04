"""
---------------
LEVEL STRUCTURE
---------------

|-Start Segments-|
Entrance > ...
Entrance Branch Start > One Way > Branch End > ...
Emtrance Branch Start > One Way > John Branch End

|-Branch Segments-|
Two Way > Branch Start > One Way  > Branch End > Two Way

|-End Segments-|
... > John
... > Branch Start > One Way > John Branch End

-----------------------------
ALGORITHM - CONSTRUCT A LEVEL
-----------------------------

1. Choose a Start Segment
2. Choose zero or more Branch Segments
3. Choose an End Segment

For any One Way, find two paths connecting both ends of the branch paths.
For any Two Way, find a path of any length connecting the two end layers.

For any other layer, determine the path being used through it.
Branch path should choose a specific path.

#TODO: change one way layer to be only one way paths?
#and only use two way layer to bridge branch paths when necessary?
#how to make it so that it uses as many one way paths as possible :think:
#if we only use one way paths the current algorithm wont be able to find a shortest possible path
#that includes two way paths
#also we have to make sure that rooms used from the two way layer are removed from the one way layer as well
#
#endpoint layers are categorized by endpoint types
#therefore if we find a shortest path AF we can prioritize
#choosing oneways when we choose the actual paths we choose
#perhaps we can do some flow that flows the proportion of oneway paths each
#edge has so that we can identify which shortest path has the highest proportions
#of one ways and therefore can be used to pick the most oneways between any two apths?
#well no because only the shortest path is left after a flow
#i guess ill just have to pick a path
#and prioritize oneways even if thats technically not the path with the most oneways
#since were prioritizing length over oneways
#maybe we can do a flow that priotizies identifying shortest path if it includes more oneways vs the actual shortest path
#but then how do we ensure the flow terminates
#question: is a longer path okay if it includes less two ways?
#prolly not, best is equal length path with more oneways should be prioritized
#but i dunno
#could look at all possible equal length paths and choose the one with the most possible oneways

"""