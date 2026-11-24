#Author: Stack man
#Date: 11/24/2026

#Re-order SD and Traversal lists in SD and FG

from json_source_destination import SourceDestinationHandler
from graph_create import FlowGraphHandler
from graph_objects import DoorNode, CombinedDoorNode
import random

def randomize_SD_FG(seed: int, SD: SourceDestinationHandler, FG: FlowGraphHandler):
    random.seed(seed)
    randomize_SD(SD) #randomize order of SD lists
    randomize_FG(FG) #randomize order of traversal lists


def randomize_SD(SD: SourceDestinationHandler):

    lists = [SD.E, SD.EB, SD.J, SD.JB, SD.BA, SD.BS, SD.BE]

    for list in lists:
        random.shuffle(list)

def randomize_FG(FG: FlowGraphHandler):

    for N in FG.nodes():

        N: DoorNode | CombinedDoorNode

        for D, traversals in N.steps.items():
            random.shuffle(traversals)
            

    