from graph_objects import DoorNode, TransitionEdge, CombinedDoorNode
from colors import CAUTION, RESET, ERROR
from settings import TraversalMode
from enums import StartExitType, DoorDir

def transition_edges_from_nodes(nodes: list[DoorNode], traversal_mode: TraversalMode):
    #for every EXIT node, look at the transition matrix and create a TransitionEdge to the corresponding START nodes
    print(f"{CAUTION} Using Traversal Mode {RESET}{traversal_mode}{CAUTION} to create the graph!{RESET}")

    #TODO: implement other modes as specified in settings.py
    match traversal_mode:
        case TraversalMode.MATCHING_PERFECT:
            return transition_edges_from_nodes_matching_perfect(nodes)
        case TraversalMode.ARBITRARY_NO_RESTRICTIONS:
            return transition_edges_from_arbitrary_no_restrictions(nodes)
        case TraversalMode.DEBUG:
            return transition_edges_from_nodes_debug(nodes)
        case _ :
            print(f"{ERROR} ERROR: Traversal Mode {traversal_mode} not implemented in transition_edges_from_nodes_and_matrix() in rooms_to_graphs.py{RESET}")
            return []

def get_existing_node(node: DoorNode, door_nodes: list[DoorNode]):
    return next((N for N in door_nodes if N == node), node )

#Match transitions with the same type and consistent directions
def transition_edges_from_nodes_matching_perfect(nodes: list[DoorNode]):

    edges = []

    for node in nodes:

        if (node.se_type == StartExitType.EXIT):
            other_type = node.door_type
            other_dir = flip_dir(node.door_dir)

            #recreate the matching node then get the actual node object from nodes
            other_node = DoorNode(other_type, other_dir, StartExitType.START)
            #cast to match the expected type while mainting DoorNode for this func
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