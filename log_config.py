#Author: Stack Man
#Date: 11/16/2026

import logging

class FileStyleFilter(logging.Filter):
    # Map specific filenames to (indent_spaces, prefix_tag)
    FILE_STYLES = {
        "json_to_objects.py":       ("", "[JSON] "),
        "graph_flow.py":            ("", "[FLOW] "),
        "graph_from_rooms.py":      ("", "[GRAPH] "),
        "level_generate_recursive.py":  ("", "[GEN]"),
        "level_segment_generator.py":   ("", "[SEG]"),
        "level_bridge.py" :             ("", "[BRIDGE]"),
        "level_room_path_generator.py": ("", "[ROOMPATH]"),
        "level_get_traversal.py":       ("", "[TRAVERSAL]"),
        "level_select_rooms.py":        ("", "[SELECTION]"),
        "level_grow.py":       ("", "[GROW] "),
        "level_clean_replenish.py":       ("", "[CLEAN] "),
        "graph_impossible_booking.py":       ("", "[DB] "),
    }

    def filter(self, record):
        indent, prefix = self.FILE_STYLES.get(
            record.filename, ("", "[OTHER] ")
        )

        record.custom_indent = indent
        record.custom_prefix = prefix

        # Pad message to a fixed width
        record.padded_message = f"{record.getMessage():<80}"

        return True

# Configure handler and formatter using your custom attributes
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(levelname)-7s | %(custom_indent)s%(custom_prefix)s"
    "%(padded_message)s | %(funcName)s"
)
handler.setFormatter(formatter)
handler.addFilter(FileStyleFilter())

# Apply to the root logger so all files inherit it
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(handler)

logging.basicConfig(level=logging.DEBUG)

logging.disable()