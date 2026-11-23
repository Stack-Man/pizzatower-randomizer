#Author: Stack Man
#Date: 11/1/2026

#Categorize Transitions and Paths into a generalized Node and Edge graph.
#Separate edges into three graphs: two-way paths only (TW), two-way or one-way pizza time paths (OWPT), and two way or one-way not pizza time paths (OWNPT).

from json_objects import Room, Path
from graph_objects import DoorNode, PathEdge, TransitionEdge, CombinedDoorNode, EdgeTraversal
from settings import TraversalMode
from enums import PathTime, RoomType, StartExitType, TraversalType, DoorType
from graph_transition_edge import transition_edges_from_nodes
import networkx as nx
from copy import deepcopy

from perf_counter import start_perf, end_perf, PerfType

class FlowGraphHandler():
    def __init__(self, G: nx.DiGraph):
        self.G = G
        #store depleted edges so next time we get a traversal we can update the traversals
        self.depleted_edges: list[PathEdge] = [] 
        self.changed_last_round = True 
        self.selected_rooms: list[str] = []

        self.edge_to_traversals: dict[PathEdge, list[EdgeTraversal]] = {}

        #Construct an index of PathEdge to the traversal that contain it, for fast lookup
        #during impossible booking
        #for N in self.nodes():
           #N : DoorNode | CombinedDoorNode
            #for D, traversals in N.steps.items():

                #traversals: list[EdgeTraversal]

                #for T in traversals:
                    #for edge in T:
                        #if (type(edge) == PathEdge):
                            #self.edge_to_traversals.setdefault(edge, []).append(T)

    def nodes(self):
        return self.G.nodes()

    def edges(self):
        return self.G.edges()

    def predecessors(self, N):
        return self.G.predecessors(N)

    def successors(self, N):
        return self.G.successors(N)

    def get_edge_data(self, U, V):
        return self.G.get_edge_data(U, V)

    def path_count(self):

        i = 0

        for U, V in self.edges():
            obj = self.get_edge_data(U, V)["object"]

            if (type(obj) == PathEdge):
                i += len(obj.TW) + len(obj.OW) + len(obj.NPT) + len(obj.PT)

        return i      

def rooms_to_graph(rooms: list[Room], traversal_mode : TraversalMode = TraversalMode.MATCHING_PERFECT ):
    start_perf(PerfType.GRAPH)
    path_edges, nodes = rooms_to_edges_and_nodes(rooms)
    transition_edges = transition_edges_from_nodes(nodes, traversal_mode)

    path_edges.extend(transition_edges)
    edges = path_edges

    print(f"{len(rooms)} rooms to {len(nodes)} nodes and {len(edges)} edges")

    graph = graph_from_nodes_and_edges(nodes, edges)

    end_perf(PerfType.GRAPH)
    return FlowGraphHandler(graph)

def get_existing_node(node: DoorNode | CombinedDoorNode, door_nodes: list[DoorNode | CombinedDoorNode]):
    return next((N for N in door_nodes if N == node), node )

def rooms_to_edges_and_nodes(rooms: list[Room]):

    door_nodes = []
    paths_by_path_edge : dict[PathEdge, list[Path]] = {}

    #categorize every path by edge type
    for room in rooms:

        for path in room.paths:

            #skip paths with a leveldoor, leveldoor will never be used for the flow
            if (path.start_door.door_type == DoorType.LEVELDOOR or path.exit_door.door_type == DoorType.LEVELDOOR):
                continue

            edge : PathEdge = path_to_edge(path)

            #replace the recreated node objects with ones already in the graph, if it exists
            edge.start_node = get_existing_node(edge.start_node, door_nodes)
            edge.end_node = get_existing_node(edge.end_node, door_nodes)

            #Exclude non normal rooms from the flow graph
            #but do include their nodes for TransitionEdges
            if (edge not in paths_by_path_edge or room.room_type != RoomType.NORMAL):

                #only add edges from normal rooms to the graph
                if (room.room_type == RoomType.NORMAL):
                    paths_by_path_edge[edge] = []

                #whenever we add a new edge, check if its nodes are already added
                if (edge.start_node not in door_nodes):
                    door_nodes.append(edge.start_node)

                if (edge.end_node not in door_nodes):
                    door_nodes.append(edge.end_node)

            if (room.room_type == RoomType.NORMAL):
                paths_by_path_edge[edge].append(path)

    path_edges = []

    #then populate those edges with the paths
    #seperate paths by traversal time
    for path_edge, paths in paths_by_path_edge.items():

        pathsTWANY, pathsOWANY, pathsPT, pathsNPT = categorize_paths_by_traversal_time(paths)

        path_edge.set_paths(pathsTWANY, pathsOWANY, pathsPT, pathsNPT)

        path_edges.append(path_edge)

    return path_edges, door_nodes

def categorize_paths_by_traversal_time(paths: list[Path]):
    pathsTWANY = []
    pathsOWANY = []
    pathsPT = []
    pathsNPT = []

    for path in paths:

        if (path.get_path_time() == PathTime.BOTH):
            if (not path.oneway):
                pathsTWANY.append(path)
            else:
                pathsOWANY.append(path)
        elif (path.get_path_time() == PathTime.NOTPIZZATIME):

            pathsNPT.append(path)
        else:
            pathsPT.append(path)

    return pathsTWANY, pathsOWANY, pathsPT, pathsNPT

def path_to_edge(path: Path):
    start_node, exit_node = path_to_nodes(path)
    return PathEdge(start_node, exit_node)

def path_to_nodes(path: Path):

    start_type = path.start_door.get_type_as_tuple()
    exit_type = path.exit_door.get_type_as_tuple()

    return DoorNode(start_type[0], start_type[1], StartExitType.START), DoorNode(exit_type[0], exit_type[1], StartExitType.EXIT)

def graph_from_nodes_and_edges(nodes: list[DoorNode|CombinedDoorNode], edges: list[PathEdge|TransitionEdge]):

    graph = nx.DiGraph()

    for node in nodes:
        graph.add_node(node)

    for edge in edges:
        graph.add_edge(edge.start_node, edge.end_node, object=edge)

    return graph


