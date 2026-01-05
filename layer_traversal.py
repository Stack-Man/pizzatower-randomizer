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

--------------------
TODO LIST:
--------------------
Before we layer traverse:

3. Update choose_path to have option to prioritize oneways when possible
4. update path_grow and path_find to alert all other layers when a room is removed or added so those layers can do the same and reflow
5. update path_find and path_grow to have an option to prioritize of all equal length paths, teh one with the most possible oneways (hard)

"""