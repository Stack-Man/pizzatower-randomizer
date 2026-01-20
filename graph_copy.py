class FakeInnerNode():
    def __init__(self):
        self.door_type = None
        self.door_dir = None
        self.start_exit_type = None

class FakeNode():
    def __init__(self, type, dir, start_exit_type):
        self.inner_id = FakeInnerNode()
        self.inner_id.door_type = type
        self.inner_id.door_dir = dir
        self.inner_id.start_exit_type = start_exit_type

from path_objects import Endpoint
import networkx as nx


def copy_graph(G):
    
    new_G = nx.DiGraph()

    node_map = {} #used because we want the edges to use the new node objects not the old ones

    # Copy nodes
    for old_N in G.nodes():
        fakenode = FakeNode(
            old_N.door_type,
            old_N.door_dir,
            old_N.start_exit_type
        )

        new_N = Endpoint(fakenode)
        new_N.steps = old_N.steps.copy()

        node_map[old_N] = new_N
        new_G.add_node(new_N)

    # Copy edges using mapped nodes
    for u, v in G.edges():
        new_G.add_edge(node_map[u], node_map[v])

    copy_graph_attributes(G, new_G)
    return new_G

def copy_graph_attributes(G, new_G):
    new_G.all_paths = G.all_paths.copy()
    
    new_G.readded_rooms = G.readded_rooms.copy()
    new_G.removed_rooms = G.removed_rooms.copy()
    
    new_G.removed_paths_by_room_and_endpoints = G.removed_paths_by_room_and_endpoints.copy()
    
    new_G.updated_since_last_flow = G.updated_since_last_flow
    
    new_G.hidden_rooms = G.hidden_rooms.copy()
    
    new_G.hidden_edges = G.hidden_edges.copy()
    
    new_G.unhidden_rooms = G.unhidden_rooms.copy()
    new_G.unhidden_edges = G.unhidden_edges.copy()
    
    new_G.name = G.name
