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
        
        self.steps["NONE"] = "NONE"
    
    def __str__(self):
        return f"{self.start_exit_type} {self.door_type} {self.door_dir}"
    
    def __eq__(self, other):
        return self.door_type == other.door_type and self.door_dir == other.door_dir and self.start_exit_type == other.start_exit_type
    
    def __hash__(self):
        return hash((self.door_type, self.door_dir, self.start_exit_type))