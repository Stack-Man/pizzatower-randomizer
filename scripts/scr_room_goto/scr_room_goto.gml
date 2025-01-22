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

	if (global.panic && global.fill < 30 * 12)
	{
		global.fill = 30 * 12; //extend time for long levels
	}

	if (ds_map_exists(global.transition_map, current_room) && !(current_room == tower_entrancehall && !global.panic)
	&& !(_room == global.leveltorestart && obj_player.targetDoor == "A") //allow normal goto if destination is the start of the level with target A
	&& !(_room == boss_pizzaface && obj_player.targetDoor == "B") //or B if pizzaface
	)
	{
		var destinations = ds_map_find_value(global.transition_map, current_room);
		
		if (ds_map_exists(destinations, current_targetDoor) )
		{
			var destination = ds_map_find_value(ds_map_find_value(global.transition_map, current_room), current_targetDoor);
	
			var new_room_id = ds_map_find_value(destination, "roomid");
			var new_targetDoor = ds_map_find_value(destination, "letter");
			
			obj_player.targetDoor = new_targetDoor;

			var msg = concat("Tried to go from ", room_get_name(current_room), " ", current_room, " ", current_targetDoor, " to ", room_get_name(new_room_id), " ", new_room_id, " ", new_targetDoor);
			global.room_msg = msg;
			show_debug_message( msg );
			
			room_goto(new_room_id);
			
			with (obj_randomizer) //trigger the enter room logic
			{
				var player_hsp = 0;
				var player_movespeed = 0;
				
				with (obj_player1)
				{
					player_hsp = hsp;
					player_movespeed = movespeed;
				}
				
				saved_hsp = player_hsp;
				saved_movespeed = player_movespeed;
				
				alarm[0] = 2; //Longer delay so that objects have a chance to set their targetDoor in their step eventa
				alarm[1] = 2; //clear and add new powerups
			}

		}
		else
		{
			var msg = concat("Returning to same room ", room_get_name(current_room), " ", current_room, " current door: ", current_targetDoor);
			global.room_msg = msg;
			show_debug_message(msg);
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
