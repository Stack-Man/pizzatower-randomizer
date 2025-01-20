// @description remove unused transitions


//upon entering the room, remove unused transitions and put obj_solid in place of hallways

//TODO: deleting obj_geromedoor leaves behind an obj_door that crashes the game (in pizzascape?)
//TODO: delete secret eyes

alarm[2] = 2;

with (obj_lapportal)
{
	instance_destroy(self);
}

with (obj_door)
{
	if (!variable_instance_exists(self, "targetRoom"))
		instance_destroy(self);
}

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
			var orginal_depth = depth;
			var orginal_layer = layer;
			
			with (instance_create_depth(x, y, depth, obj_closedboxofpizza))
			{
				image_xscale = xscale;
				image_yscale = yscale;
				depth = orginal_depth;
				layer = orginal_layer;
			}
			
			instance_destroy(self);
		}	
	}

	with (obj_geromedoor)
	{
		if (!ds_map_exists(room_transitions, targetDoor))
			instance_destroy(self);
	}
	
	with (obj_taxi)
	{
		if (!ds_map_exists(room_transitions, "taxi"))
			instance_destroy(self);
	}
	
	/*with (obj_spaceshuttle)
	{
		if (!ds_map_exists(room_transitions, "rocket"))
			instance_destroy(self);
	}*/
	
	with (obj_secretportal)
	{
		if (!ds_map_exists(room_transitions, "secret"))
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
			var orginal_depth = depth;
			var orginal_layer = layer;
			
			with (instance_create_depth(x, y, depth, obj_hallway_blocked))
			{
				image_xscale = xscale;
				image_yscale = yscale;
				depth = orginal_depth;
				layer = orginal_layer;
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
			var orginal_depth = depth;
			var orginal_layer = layer;
			
			with (instance_create_depth(x, y, depth, obj_verticalhallway_blocked))
			{
				image_xscale = xscale;
				image_yscale = yscale;
				depth = orginal_depth;
				layer = orginal_layer;
			}
			
			instance_destroy(self);
		}	
	}
}