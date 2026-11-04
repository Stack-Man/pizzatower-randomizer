#Author: Stack Man
#Date: 11/1/2026

#Categorize Transitions and Paths into a generalized Node and Edge graph.
#Separate edges into three graphs: two-way paths only (TW), two-way or one-way pizza time paths (OWPT), and two way or one-way not pizza time paths (OWNPT).

from objects import Room, Path
from graph_objects import DoorNode, PathEdge, StartExitType, TransitionEdge
from settings import GRAPH_TRAVERSAL_MODE, TraversalMode
from colors import ERROR, RESET, CAUTION
from enums import DoorDir, PathTime, RoomType
import networkx as nx

def rooms_to_graph(rooms: list[Room]):
    path_edges, nodes = rooms_to_edges_and_nodes(rooms)
    transition_edges = transition_edges_from_nodes(nodes)

    graph = graph_from_nodes_and_edges(nodes, path_edges, transition_edges)

    return graph

def get_existing_node(node: DoorNode, door_nodes: list[DoorNode]) -> DoorNode:
    return next(
        (existing for existing in door_nodes if existing == node),
        node
    )

def rooms_to_edges_and_nodes(rooms: list[Room]):

    door_nodes = []
    paths_by_path_edge : dict[PathEdge, list[Path]] = {}

    #categorize every path by edge type
    for room in rooms:

        #Exclude non normal rooms from the flow graph
        if room.room_type is not RoomType.NORMAL:
            continue

        for path in room.paths:

            edge : PathEdge = path_to_edge(path)

            #replace the recreated node objects with ones already in the graph, if it exists
            edge.start_node = get_existing_node(edge.start_node, door_nodes)
            edge.end_node = get_existing_node(edge.end_node, door_nodes)

            if (edge not in paths_by_path_edge):
                paths_by_path_edge[edge] = []

                #whenever we add a new edge, check if its nodes are already added
                if (edge.start_node not in door_nodes):
                    door_nodes.append(edge.start_node)

                if (edge.end_node not in door_nodes):
                    door_nodes.append(edge.end_node)


            paths_by_path_edge[edge].append(path)

    path_edges = []

    #then populate those edges with the paths
    #seperate paths by traversal time
    for path_edge, paths in paths_by_path_edge.items():

        pathsTWANY, pathsOWANY, pathsPT, pathsNPT = categorize_paths_by_traversal_time(paths)

        path_edge.pathsTWANY = pathsTWANY
        path_edge.pathsOWANY = pathsOWANY
        path_edge.pathsPT = pathsPT
        path_edge.pathsNPT = pathsNPT

        path_edges.append(path_edge)

    return path_edges, door_nodes

def categorize_paths_by_traversal_time(paths: list[Path]):
    pathsTWANY = []
    pathsOWANY = []
    pathsPT = []
    pathsNPT = []

    for path in paths:

        if (path.path_time() == PathTime.BOTH):
            if (not path.oneway):
                pathsTWANY.append(path)
            else:
                pathsOWANY.append(path)
        elif (path.path_time() == PathTime.NOTPIZZATIME):

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

def graph_from_nodes_and_edges(nodes: list[DoorNode], path_edges: list[PathEdge], transition_edges: list[TransitionEdge]):

    graph = nx.DiGraph()

    for node in nodes:
        graph.add_node(node)

    for edge in path_edges:
        graph.add_edge(edge.start_node, edge.end_node, object=edge)

    for edge in transition_edges:
        graph.add_edge(edge.start_node, edge.end_node, object=edge)

    return graph

def transition_edges_from_nodes(nodes: list[DoorNode]):
    #for every EXIT node, look at the transition matrix and create a TransitionEdge to the corresponding START nodes
    print(f"{CAUTION} Using Traversal Mode {RESET}{GRAPH_TRAVERSAL_MODE}{CAUTION} to create the graph!{RESET}")

    #TODO: implement other modes as specified in settings.py
    match GRAPH_TRAVERSAL_MODE:
        case TraversalMode.MATCHING_PERFECT:
            return transition_edges_from_nodes_matching_perfect(nodes)
        case TraversalMode.ARBITRARY_NO_RESTRICTIONS:
            return transition_edges_from_arbitrary_no_restrictions(nodes)
        case TraversalMode.DEBUG:
            return transition_edges_from_nodes_debug(nodes)
        case _ :
            print(f"{ERROR} ERROR: Traversal Mode {GRAPH_TRAVERSAL_MODE} not implemented in transition_edges_from_nodes_and_matrix() in rooms_to_graphs.py{RESET}")
            return []

#Match transitions with the same type and consistent directions
def transition_edges_from_nodes_matching_perfect(nodes: list[DoorNode]):

    edges = []

    for node in nodes:

        if (node.se_type == StartExitType.EXIT):
            other_type = node.door_type
            other_dir = flip_dir(node.door_dir)

            #recreate the matching node then get the actual node object from nodes
            other_node = DoorNode(other_type, other_dir, StartExitType.START)
            other_node = get_existing_node(other_node, nodes) 

            edge = TransitionEdge(node, other_node)
            edges.append(edge)

    return edges

def transition_edges_from_arbitrary_no_restrictions(nodes: list[DoorNode]):

    edges = []

    for A in nodes:

        for B in nodes:

            #match all exits to all starts
            if (A.se_type == StartExitType.EXIT and B.se_type == StartExitType.START):
                edge = TransitionEdge(A, B)
                edges.append(edge)

    return edges

def transition_edges_from_nodes_debug(nodes: list[DoorNode]):
    return []

def flip_dir(dir: DoorDir):
    match dir:
        case DoorDir.LEFT:
            return DoorDir.RIGHT
        case DoorDir.RIGHT:
            return DoorDir.LEFT
        case DoorDir.UP:
            return DoorDir.DOWN
        case DoorDir.DOWN:
            return DoorDir.UP
        case _:
            return dir