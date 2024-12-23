function scr_room_goto(_room)
{
	// live_enabled was off when building
	
	/*
	if live_enabled
		room_goto_live(_room);
	else
	*/
	
	//Transition map is a map of maps
	//Key : Value is room_index : Map of letters
	//Letter Map
	//Key : Value is letter (string) : Destination Map
	//Destination Map
	//destionationvalues.roomid : room index
	//destinationvalues.letter : letter (string)
	
	//TODO: door to hallway transitions cause you to immediately return through the hallway
	
	var current_targetDoor = obj_player.targetDoor;
	
	if (ds_map_exists(global.transition_map, room) )
	{
		var destinations = ds_map_find_value(global.transition_map, room);
		
		if (ds_map_exists(destinations, current_targetDoor) )
		{
			var destination = ds_map_find_value(ds_map_find_value(global.transition_map, room), current_targetDoor);
	
			var new_room_id = ds_map_find_value(destination, destinationvalues.roomid);
			var new_targetDoor = ds_map_find_value(destination, destinationvalues.letter);
	
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
