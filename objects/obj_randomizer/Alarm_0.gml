// @description remove unused transitions
//upon entering the room, remove unused transitions and put obj_solid in place of hallways

alarm[2] = 2;

if (instance_exists(obj_keydoor))
{
	var create = false;
	
	with (obj_keydoor)
	{
		create = sprite_index == spr_doorkeyopen;
	}
	
	if (create)
		rd_key(true);
}
else
{
	rd_key(false);
}

if (instance_exists(obj_geromedoor))
{
	var create = false;
	
	with (obj_geromedoor)
	{
		create = sprite_index == spr_gerome_opendoor;;
	}
	
	if (create)
		rd_gerome(true);
}
else
{
	rd_gerome(false);
}


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