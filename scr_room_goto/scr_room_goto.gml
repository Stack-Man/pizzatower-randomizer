function scr_room_goto(_room)
{	
	//Transition map is a map of maps
	//Key : Value is room_index : Map of letters
	
	//Letter Map
	//Key : Value is letter (string) : Destination Struct
	
	//Destination Struct
	//roomid : room index
	//letter : letter (string)
	
	//TODO: account for non matching transitions,a ccount for unused transitions
	
	var current_targetDoor = obj_player.targetDoor;
	
	if (ds_map_exists(global.transition_map, room) )
	{
		var destinations = ds_map_find_value(global.transition_map, room);
		
		if (ds_map_exists(destinations, current_targetDoor) )
		{
			var destination = ds_map_find_value(ds_map_find_value(global.transition_map, room), current_targetDoor);
	
			var new_room_id = destination.roomid;
			var new_targetDoor = destination.letter;
	
			show_debug_message( concat("Tried to go from ", room_get_name(room), " ", obj_player.targetDoor, " to ", room_get_name(new_room_id), " ", new_targetDoor) );
	
			obj_player.targetDoor = new_targetDoor;
			
			room_goto(new_room_id);
			
			
		}
		else
		{
			room_goto(_room);
		}
		
	}
	else
	{
		room_goto(_room);
	}
	
	
	
}
