"""
------------
GRAPH INIT
------------
"""
from path_mapping import categorize_paths
from path_flow import flow
import threading
from graph_copy import copy_graph

def layer_to_endpoints(G):
    #creates new Endpoint nodes for the graph G, 
    #therefore  there is no conflict between different Gs with
    #Endpoints of the same ID
    paths = categorize_paths(G) 
    
    ep_graph = construct_endpoint_graph(paths, None)
    
    G_init_attributes(ep_graph, paths)
    
    flowed = flow(ep_graph) #initialize flow
    
    return flowed

def G_init_attributes(G, all_paths):
    G.all_paths = all_paths
    
    G.readded_rooms = []
    G.removed_rooms = []
    
    G.removed_paths_by_room_and_endpoints = {}
    
    G.updated_since_last_flow = True
    
    G.hidden_rooms = []
    G.unhidden_rooms = []
    
    G.hidden_edges = []
    G.unhidden_edges = []

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
        
        if start_point not in start_points:
            start_points.append(start_point)
        
        if exit_point not in exit_points:
            exit_points.append(exit_point)
        
        endpoint_graph.add_edge(start_point, exit_point)
    
    print("CONNECTING ENDPOINTS")
    
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
                
                print("     CONNECT ", str(ep), " TO ", str(sp))
    
    """
     N:  EXIT HALL LEFT
             F:  EXIT HALL LEFT  step:  0  hid:  0
             F:  START HALL RIGHT  step:  1  hid:  0
     N:  EXIT BOX DOWN
         F:  EXIT BOX DOWN  step:  0  hid:  0
         F:  START HALL RIGHT  step:  1  hid:  0
     N:  EXIT FALL UP
         F:  EXIT FALL UP  step:  0  hid:  0
         F:  START HALL RIGHT  step:  1  hid:  0
     N:  EXIT HALL RIGHT
         F:  EXIT HALL RIGHT  step:  0  hid:  0
         F:  START HALL LEFT  step:  1  hid:  0
     N:  EXIT BOX UP
         F:  EXIT BOX UP  step:  0  hid:  0
         F:  START HALL LEFT  step:  1  hid:  0
     N:  EXIT DOOR NONE
         F:  EXIT DOOR NONE  step:  0  hid:  0
         F:  START HALL LEFT  step:  1  hid:  0
     N:  EXIT FALL DOWN
         F:  EXIT FALL DOWN  step:  0  hid:  0
         F:  START FALL UP  step:  1  hid:  0
"""
    
    #TODO: for some reason the flow looks like this, is the graph reverse not correct?
    
    #exit hall left > start hall right
    #exit box down  > start hall right
    #exit fall up  > start hall right
    #exit hall right  > start hall left
    #exit box up  > start hall left
    #exit door none  > start hall left
    #exit fall down  > start fall up <--- only this one is correct
    
    
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
def temp_remove_room_by_path(G, path):
    temp_G = copy_graph(G)
    
    remove_room_by_path(temp_G, path)
    
    return temp_G

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

MIN_ROOMS_TO_HIDE = -1 #TODO: parameterize, set to -1 to disable

def remove_paths_of_room_by_endpoint(G, room_name, endpoint_key):
    paths = G.all_paths[endpoint_key]

    #no paths to remove
    if len(paths) == 0:
        return
    
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
        G.remove_edge(endpoint_key[0], endpoint_key[1])
        G.updated_since_last_flow = True
        
    elif len(kept_paths) <= MIN_ROOMS_TO_HIDE:
        #hide edge and hide rooms in this edge
        G.hidden_edges.append(endpoint_key)
        hide_rooms_by_paths(G, kept_paths)

def remove_rooms_by_endpoint_path(G, endpoint_path):
    for endpoint_path_pair in endpoint_path:
        path = endpoint_path_pair[1]
        
        if path:
            remove_room_by_path(G, path)

def remove_endpoint(G, endpoint):
    G.remove_node(endpoint)

def remove_rooms_by_endpoint_path(G, endpoint_path):
    by_endpoint_path(G, endpoint_path, remove_room_by_room)

def by_endpoint_path(G, endpoint_path, action):
    threads = []
    used_room_names = []
    
    for _, path in endpoint_path:
        
        if path:
            room_name = path.room_name
            
            #only create 1 thread per room
            if room_name not in used_room_names:
                
                used_room_names.append(room_name)
                
                t = threading.Thread(target=action, args=(G, room_name))
                threads.append(t)
                t.start()
    
    for t in threads:
        t.join()

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
    print("add by endpoint path")
    by_endpoint_path(G, endpoint_path, add_room_by_room)

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
            G.updated_since_last_flow = True
            
        #check if readding these paths disqualifies any other room from being hidden
        unhide_rooms_by_endpoint(G, endpoint_key) 
        
        #if length is still under the hide threshold
        #after the previous unhide check, hide it
        if len(G.all_paths[endpoint_key]) <= MIN_ROOMS_TO_HIDE:
            hide_rooms_by_paths(G, G.all_paths[endpoint_key])
    
    del G.removed_paths_by_room_and_endpoints[room_name] #finished with entry

"""
--------------
UPDATE OTHER G
--------------
"""

#Update all other G to remove/readd/hide/unhide rooms removed/readded/hidden/unhidden in G
def update_other_G(G, others):

    for O in others:
        
        #readd first then remove
        for room in G.readded_rooms:
            add_room_by_room(O, room)
        
        for room in G.removed_rooms:
            remove_room_by_room(O, room)
    
        #unhide first then rehide
        for room in G.unhidden_rooms:
            O.hidden_rooms.remove(room)
        
        for edge in G.unhidden_edges:
            O.hidden_edges.remove(edge)
        
        for room in G.hidden_rooms:
            O.hidden_rooms.append(room)
        
        for edge in G.hidden_edges:
            O.hidden_edges.append(edge)

    #clear because these lists were only used to update other Gs
    G.readded_rooms = []
    G.unhidden_rooms = []
    G.unhidden_edges = []

"""
----------
HIDE ROOMS
----------

Hide edges with less paths than MIN_ROOMS_TO_HIDE by marking them as hidden in G.hidden_edges as (endpoint, endpoint)
Hide rooms with paths in those hidden edges by appending them to G.hidden_rooms
Paths from hidden rooms are deprioritized in path_traversal.choose_path
The only time a hidden path should be REQUIRED is if the path is in a hidden edge
"""

def temp_unhide_rooms(G, rooms):
    #temp_G = deepcopy(G)
    if rooms is None:
        raise RuntimeError("Tried to unhide with list as None")
    
    temp_G = copy_graph(G)
    #print("unhide by temp unhide")
    unhide_rooms(temp_G, rooms)
    return temp_G

def unhide_rooms(G, rooms):
    to_readd = []
    
    #remove all marked rooms from hidden first
    for room_name in rooms:
        if room_name in G.hidden_rooms:
            G.hidden_rooms.remove(room_name)
            G.unhidden_rooms.append(room_name)


def hide_rooms_by_paths(G, paths):
    for p in paths:
        hide_room_by_path(G, p)

def hide_room_by_path(G, path):
    room_name = path.room_name
    hide_room_by_room(G, room_name)
    

#Edges are hidden in remove room
def hide_room_by_room(G, room_name):
    if room_name not in G.hidden_rooms:
        G.hidden_rooms.append(room_name)

#called by add room
def unhide_rooms_by_endpoint(G, endpoint_key):

    #if we still meet the hide requirement
    #then we dont need to unhide anything
    if len(G.all_paths[endpoint_key]) <= MIN_ROOMS_TO_HIDE:
        return

    G.hidden_edges.remove(endpoint_key)
    G.unhidden_edges.append(endpoint_key)
    
    rooms_to_unhide = []

    #paths of hidden rooms were not actually removed
    for path in G.all_paths[endpoint_key]:
        
        p_room_name = path.room_name
        
        if p_room_name not in rooms_to_unhide:
            
            if p_room_name in G.hidden_rooms: #unhide rooms that were hidden
                rooms_to_unhide.append(p_room_name)
    
    unhide_rooms(G, to_unhide)



def print_graph_attributes(G):
    print(f"all paths: {len(G.all_paths)}")
    print(f"readded_rooms: {len(G.readded_rooms)}")
    print(f"removed_rooms: {len(G.removed_rooms)}")
    print(f"removed_paths_by_room_and_endpoints: {len(G.removed_paths_by_room_and_endpoints)}")
    print(f"updated_since_last_flow: {str(G.updated_since_last_flow)}")
    print(f"hidden_rooms: {len(G.hidden_rooms)}")

        