//upon entering the room, remove unused transitions and put obj_solid in place of hallways

//TODO: deleting obj_geromedoor leaves behind an obj_door that crashes the game (in pizzascape?)
//TODO: delete secret eyes

alarm[2] = 2;

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
			
			with (instance_create_depth(x, y, depth, obj_closedboxofpizza))
			{
				image_xscale = xscale;
				image_yscale = yscale;
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
			//var xscale = image_xscale;
			//var yscale = image_yscale;
			
			/*with (instance_create_depth(x, y, depth, obj_solid))
			{
				image_xscale = xscale * 100;
				image_yscale = yscale * 100;
				visible = true;
			}*/
			
			enable = false;
			solid = true;
			
			//instance_destroy(self);
		}
	}

	//TODO: proper blockage
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