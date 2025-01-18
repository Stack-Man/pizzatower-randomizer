function scr_room_goto(_room)
{	
	//Transition map is a map of maps
	//Key : Value is room_index : Map of letters
	
	//Letter Map
	//Key : Value is letter (string) : Destination Struct
	
	//Destination Struct
	//roomid : room index
	//letter : letter (string)

	var current_targetDoor = obj_player.targetDoor;
	
	var current_room = room;

	if (ds_map_exists(global.transition_map, current_room) && !(current_room == tower_entrancehall && !global.panic)
	&& !(_room == global.leveltorestart && obj_player.targetDoor == "A") //allow normal goto if destination is the start of the level with target A
	&& !(_room == boss_pizzaface && obj_player.targetDoor == "B") //or B if pizzaface
	)
	{
		var destinations = ds_map_find_value(global.transition_map, current_room);
		
		if (ds_map_exists(destinations, current_targetDoor) )
		{
			var destination = ds_map_find_value(ds_map_find_value(global.transition_map, current_room), current_targetDoor);
	
			//var new_room_id = destination.roomid;
			//var new_targetDoor = destination.letter;
			
			var new_room_id = ds_map_find_value(destination, "roomid");
			var new_targetDoor = ds_map_find_value(destination, "letter");
			
			show_debug_message( concat("Tried to go from ", room_get_name(current_room), " ", obj_player.targetDoor, " to ", room_get_name(new_room_id), " ", new_targetDoor) );
			obj_player.targetDoor = new_targetDoor;

			room_goto(new_room_id);
			
			with (obj_randomizer) //trigger the enter room logic
			{
				alarm[0] = 2; //Longer delay so that objects have a chance to set their targetDoor in their step eventa
				alarm[1] = 2; //clear and add new powerups
			}

		}
		else
		{
			show_debug_message( concat("Returning to same room ", room_get_name(current_room), " ", obj_player.targetDoor, " to ", room_get_name(current_room), " ", obj_player.targetDoor) );
			room_goto(current_room);
		}
		
	}
	else
	{
		room_goto(_room);
		
		with (obj_randomizer) //trigger the enter room logic, mostly for entrance rooms
		{
			alarm[0] = 2;
		}
	}
	
	
	
}
