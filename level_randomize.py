#Author: Stack man
#Date: 11/24/2026

#Re-order SD and Traversal lists in SD and FG

from json_source_destination import SourceDestinationHandler
from graph_create import FlowGraphHandler
from graph_objects import DoorNode, CombinedDoorNode
import random

import logging as log

def set_seed(seed: int):

    log.debug("Set seed as %s", seed)
    
    random.seed(seed)

def randomize_SD_FG(SD: SourceDestinationHandler, FG: FlowGraphHandler):
    randomize_SD(SD) #randomize order of SD lists
    randomize_FG_deterministic(FG) #randomize order of traversal lists


def randomize_SD(SD: SourceDestinationHandler):
    lists = [SD.E, SD.EB, SD.J, SD.JB, SD.BA, SD.BS, SD.BE]

    for list in lists:
        random.shuffle(list)


def randomize_FG_deterministic(FG: FlowGraphHandler):

    #use sorted() to ensure consistent order every time
    for N in sorted(FG.nodes(), key=lambda x: x._hash):

        #log.debug("Randomizing %s", N)

        N: DoorNode | CombinedDoorNode

        for D, traversals in sorted(N.steps.items(), key=lambda x: x[0]._hash):

            #log.debug("     Randomizing %s of %s", D, N)
            random.shuffle(traversals)
            

    