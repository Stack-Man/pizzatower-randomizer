import os
from constants import JSON_NAMES

def parse_level_jsons():

    for json_name in JSON_NAMES:
        dir = "/json/" + json_name + ".json"

        if not os.path.exists(dir):
            continue

        with open(dir, 'r') as json:
            pass

    pass