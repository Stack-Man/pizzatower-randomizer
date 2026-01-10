"""
------------
GRAPH INIT
------------
"""
from path_mapping import categorize_paths
import path_flow

def layer_to_endpoints(G):
    paths = categorize_paths(G)
    ep_graph = construct_endpoint_graph(paths, None)
    
    G_init_attributes(ep_graph, paths)
    
    flowed = path_flow.flow(ep_graph) #initialize flow
    
    return flowed

def G_init_attributes(G, all_paths):
    G.all_paths = all_paths
    
    G.readded_rooms = []
    G.removed_rooms = []
    
    G.removed_paths_by_room_and_endpoints = {}
    
    G.updated_since_last_flow = True
    
    G.hidden_rooms = []

"""
------------------
STRUCTURE OF GRAPH
------------------
Construct a directed bipartite graph with two sets: Start Endpoints and Exit Endpoints
Start > Exit edges represents all paths with those types of endpoints
Exit > Start edges represent edges in the transition matrix

The Transition Matrix is a graph showing which start endpoints an exit endpoint 
is allowed to lead to in the next room
"""
import networkx as nx
from json_to_objects import flip_dir

def construct_endpoint_graph(paths, traversal_mode):

    endpoint_graph = nx.DiGraph()
    start_points = []
    exit_points = []
    
    for endpoint_pair, paths in paths.items():
        start_point = endpoint_pair[0]
        exit_point = endpoint_pair[1]
        
        start_points.append(start_point)
        exit_points.append(exit_point)
        
        endpoint_graph.add_edge(start_point, exit_point)
    
    #TODO: traversal mode
    #current basic traversal mode, connect directly to matching type, dir ignored
    
    #MODE: matching perfect
    #Match transitions with the same type and consistent directions
    for ep in exit_points:
        for sp in start_points:
            
            same_type = ep.door_type == sp.door_type
            good_dir = flip_dir(ep.door_dir) == sp.door_dir #flipped matches or no flip for type
            
            if same_type and good_dir:
                endpoint_graph.add_edge(ep, sp)
    
    
    #MODE: matching directional
    #Match transitions that have consistent directions, but possibly different types
    #TODO:
    
    #MODE: arbitrary no turnarounds
    #Match transitions in any way, but don't allow left/left, right/right, up/up, or down/down
    #TODO:
    
    #MODE: arbitrary no restrictions
    #Match transitions in any way
    #TODO:
    
   
    """
    for ep in exit_points:
        for sp in start_points:
            if ep.door_type == sp.door_type and ep.start_exit_type != sp.start_exit_type:
                endpoint_graph.add_edge(ep, sp)"""
    
    return endpoint_graph


"""
--------------------------
ADD OR REMOVE PATHS FROM G
--------------------------

If we use some path P from room R all other paths in R become unavailable.
Similarly, if we choose not to use said path, the paths of R become available again.

In any shortest path AF, as long as one valid path P for each edge remains, the path is valid.
If we use all paths of edge XY in AF, we must remove edge XY from the graph
This removal changes the shortest paths for any path AF, so we must reflow the graph.

And vice versa if we add some edge XY to G

---------------------------------------
ALGORITHM - REMOVE PATHS OF ROOM FROM G
---------------------------------------
1. Get Room R of path P
2. For every category of paths AF
3. Remove all paths R_P in all_paths[AF]
3b.Store all removed paths in dict[R][AF] for later readdition
4. If all_paths[AF] = 0, remove AF from G
5. If at least one edge was removed, Flow(G)
"""

def remove_room_by_path(G, path):
    room_name = path.room_name
    remove_room_by_room(G, room_name)

def remove_room_by_room(G, room_name):
    remove_paths_of_room(G, room_name)

def remove_paths_of_room(G, room_name):
    #stop if already removed
    if room_name in G.removed_rooms:
        return
    
    #if in readded, room was removed before
    #other Gs were updated
    if room_name in G.readded_rooms:
        G.readded_rooms.remove(room_name)
    
    G.removed_rooms.append(room_name) #track removed rooms
    G.removed_paths_by_endpoints = {} #track removed paths across threads
    
    threads = []
    
    for endpoint_key, _ in G.all_paths.items():
        t = threading.Thread(target=remove_paths_of_room_by_endpoint, args=(G, room_name, endpoint_key))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    #Fine to clear because must be empty if room not already removed
    G.removed_paths_by_room_and_endpoints[room_name] = {}
    #Update with paths removed during threaded section
    G.removed_paths_by_room_and_endpoints[room_name].update(G.removed_paths_by_endpoints)

MIN_ROOMS_TO_HIDE = 1 #TODO: parameterize, set to -1 to disable

def remove_paths_of_room_by_endpoint(G, room_name, endpoint_key):
    #no paths to remove
    if len(paths) == 0:
        return
    
    paths = G.all_paths[endpoint_key]
    
    kept_paths = []
    removed_paths = []
    
    for path in paths:
        if not path.room_name == room_name:
            kept_paths.append(path)
        else:
            #store removed path as its endpoint pair and the path
            removed_paths.append(path)
    
    G.all_paths[endpoint_key] = kept_paths
    G.removed_paths_by_endpoints[endpoint_key] = removed_paths
    
    if len(kept_paths) == 0:
        #remove edge and mark updated
        G.remove_edges(endpoint_key[0], endpoint_key[1])
        G.updated_since_last_flow = True #TODO: use this val to reflow before accessing STEPS
    elif len(kept_paths) <= MIN_ROOMS_TO_HIDE:
        #hide edge
        #hide calls remove so edges will be removed then
        hide_rooms_by_paths(G, kept_paths)

def remove_rooms_by_endpoint_path(G, endpoint_path):
    for endpoint_path_pair in endpoint_path:
        path = endpoint_path_pair[1]
        
        if path:
            remove_room_by_path(G, path)

"""
---------------------------------------
ALGORITHM - ADD PATHS OF ROOM FROM G
---------------------------------------
1. For every room R in path AF
2. For every removed path P of type XY from R
3. add P to all_paths[XY]
4. if all_paths[XY] WAS 0, add edge XY to G
5. If at least one edge was added, Flow(G)
"""
def add_rooms_by_endpoint_path(G, endpoint_path):
    threads = []
    used_room_names = []
    
    for endpoint_key, path in endpoint_path:
        
        if path:
            room_name = path.room_name
            
            #only create 1 thread per room
            if room_name not in used_room_names:
                
                used_room_names.append(room_name)
                
                t = threading.Thread(target=add_room_by_room, args=(G, room_name))
                threads.append(t)
                t.start()
    
    for t in threads:
        t.join()

def add_room_by_room(G, room_name):
    #stop if already readded
    if room_name in G.readded_rooms:
        return
    
    #no need to readd room not removed
    if room_name not in G.removed_rooms:
        return
    
    G.removed_rooms.remove(room_name)
    G.readded_rooms.append(room_name)

    #was in removed_rooms therefore should be here too
    removed_paths_by_endpoint = G.removed_paths_by_room_and_endpoints[room_name]

    for endpoint_key, paths in removed_paths_by_endpoint.items():
        
        original_length = len(G.all_paths[endpoint_key])
        G.all_paths[endpoint_key].extend(paths)
        
        if original_length == 0:
            G.add_edge(endpoint_key[0], endpoint_key[1])
            G.updated_since_last_flow = True #TODO: use this val to reflow before accessing STEPS
            
        #check if readding these paths disqualifies any other room from being hidden
        unhide_rooms_by_endpoint(G, endpoint_key)
        
        #if length is still under the hide threshold
        #after the previous unhide check, hide it
        if len(G.all_paths[endpoint_pair]) <= MIN_ROOMS_TO_HIDE:
            hide_rooms_by_paths(G, G.all_paths[endpoint_pair])
    
    del G.removed_paths_by_room_and_endpoints[room_name] #finished with entry

"""
--------------
UPDATE OTHER G
--------------
"""

#Update all other G to remove/readd/hide rooms removed/readded/hidden in G
def update_other_G(G, others):
    
    to_readd = G.readded_rooms
    to_remove = G.removed_rooms 
    to_hide = G.hidden_rooms
    
    
    #readd all to readd that's in O.removed
    for O in others:
        
        for room in to_readd:

            if room in O.hidden_rooms:
                unhide_rooms(O, [room])
            elif room in O.removed:
                add_room_by_room(O, room)
    
    #hide all in to hide
    for O in others:
    
        for room in to_hide:

            if room not in O.hidden_rooms:
                hide_room_by_room(O, room)
    
    #remove all in to remove
    for O in others:
        
        for room in to_remove:

            if room not in O.removed_rooms and room not in O.hidden_rooms:
                remove_all_room_paths_by_room(room, O)
    
    G.readded_rooms = [] #clear because we dont need to know which were readded anymore

"""
----------
HIDE ROOMS
----------
"""
from copy import deepcopy

def temp_unhide_rooms(G, rooms):
    temp_G = deepcopy(G)
    unhide_rooms(temp_G, rooms)
    return temp_G

def unhide_rooms(G, rooms):
    for room_name in rooms:
        if room_name in G.hidden_rooms:
            G.hidden_rooms.remove(room_name)
            add_room_by_room(G, room_name)

def hide_room_by_path(G, path):
    room_name = path.room_name
    hide_room_by_room(G, room_name)
    

def hide_room_by_room(G, room_name):
    if room_name not in G.hidden_rooms:
        G.hidden_rooms.append(room_name)
        remove_room_by_room(G, room_name)

def unhide_rooms_by_endpoint(G, endpoint_key):

    to_unhide = []
    
    for room_name in G.removed_paths_by_room_and_endpoints and room_name in G.hidden_rooms:
       
        removed_paths_by_endpoints = G.removed_paths_by_room_and_endpoints[room_name]
        
        if endpoint_key in removed_paths_by_endpoints:
            
            should_unhide = True
            
            for other_key in removed_paths_by_endpoints:
                
                future_length = len(removed_paths_by_endpoints[other_key]) + len(G.all_paths[other_key])
                
                #if any endpoint type readded would not end up with more than one path, do not unhide the room at all
                if not future_length > MIN_ROOMS_TO_HIDE:
                    should_unhide = False
                    break
            
            if should_unhide:
                to_unhide.append(room_name)
    
    unhide_rooms(G, to_unhide)