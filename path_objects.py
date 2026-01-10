class RoomPath():
    def __init__(self, room_name, start_letter, exit_letter, is_oneway):
        self.room_name = room_name
        self.start_letter = start_letter
        self.exit_letter = exit_letter
        self.is_oneway = is_oneway
    
    def __str__(self):
        return f"{self.room_name} {self.start_letter}{self.exit_letter}"

class Endpoint():
    def __init__(self, node):
        self.door_type = node.inner_id.door_type
        self.door_dir = node.inner_id.door_dir
        self.start_exit_type = node.inner_id.start_exit_type
        self.steps = {}
        self.next_steps = {}
        
        self.steps["NO STEPS SET"] = "NO STEPS SET"
    
    def __str__(self):
        return f"{self.start_exit_type} {self.door_type} {self.door_dir}"
    
    def __eq__(self, other):
        if not isinstance(other, Endpoint):
            return NotImplemented

        return (
            getattr(self, "door_type", None) == getattr(other, "door_type", None)
            and getattr(self, "door_dir", None) == getattr(other, "door_dir", None)
            and getattr(self, "start_exit_type", None) == getattr(other, "start_exit_type", None)
        )
    
    def __hash__(self):
        return hash((
            getattr(self, "door_type", None),
            getattr(self, "door_dir", None),
            getattr(self, "start_exit_type", None),
        ))