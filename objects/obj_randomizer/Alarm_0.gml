show_debug_message("Randomizer alarm went off");

if (ds_map_exists(global.transition_map, room_id_went_to))
{
	show_debug_message("Deleting unused transitions");
	
	var room_transitions = ds_map_find_value(global.transition_map, room_id_went_to);
	
	var arr = [];
	ds_map_keys_to_array(room_transitions, arr);
	
	for (var i = 0; i < array_length(arr); i++)
	{
		show_debug_message(concat("Used Transition: ", arr[i]) );
	}

	with (obj_door)
	{
		if (!ds_map_exists(room_transitions, targetDoor))
		{
			show_debug_message(concat("Unused Transition: ", targetDoor) );
			
			instance_destroy(self);
		}
	}

	with (obj_boxofpizza)
	{
		if (!ds_map_exists(room_transitions, targetDoor))
		{
			show_debug_message(concat("Unused Transition: ",targetDoor) );

			instance_destroy(self);
		}	
	}

	with (obj_geromedoor)
	{
		if (!ds_map_exists(room_transitions, targetDoor))
			instance_destroy(self);
	}

	with (obj_keydoor)
	{
		if (!ds_map_exists(room_transitions, targetDoor))
			instance_destroy(self);
	}

	with (obj_hallway)
	{
		show_debug_message(concat("Unused Transition: ",targetDoor) );
		
		if (!ds_map_exists(room_transitions, targetDoor))
		{
			var xscale = image_xscale;
			var yscale = image_yscale;
			
			with (instance_create_depth(x, y, depth, obj_solid))
			{
				image_xscale = xscale;
				image_yscale = yscale;
			}
			
			instance_destroy(self);
		}
	}

	with (obj_verticalhallway)
	{
		show_debug_message(concat("Unused Transition: ",targetDoor) );
		
		if (!ds_map_exists(room_transitions, targetDoor))
		{
			var xscale = image_xscale;
			var yscale = image_yscale;
			
			with (instance_create_depth(x, y, depth, obj_solid))
			{
				image_xscale = xscale;
				image_yscale = yscale;
			}
			
			instance_destroy(self);
		}
	}
}