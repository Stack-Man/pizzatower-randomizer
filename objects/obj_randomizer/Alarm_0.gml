//upon entering the room, remove unused transitions and put obj_solid in place of hallways
//TODO: first room of a level doesnt create the solids properly but still deletes the hallways


if (ds_map_exists(global.transition_map, room))
{
	var room_transitions = ds_map_find_value(global.transition_map, room);
	
	with (obj_door)
	{
		if (!ds_map_exists(room_transitions, targetDoor))
			instance_destroy(self);
	}

	with (obj_boxofpizza)
	{
		if (!ds_map_exists(room_transitions, targetDoor))
		{
			var xscale = image_xscale;
			var yscale = image_yscale;
			
			//TODO: use different object
			with (instance_create_depth(x, y, depth, obj_tutorialtargetblock))
			{
				image_xscale = xscale;
				image_yscale = yscale;
				
				visible = true;
				
				image_index = spr_closedboxofpizza;
			}
			
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