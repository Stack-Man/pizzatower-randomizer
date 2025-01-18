rd_clear_transformation();
			
if (ds_map_exists(global.powerup_map, room) )
{
	var powerup_room = ds_map_find_value(global.powerup_map, room);
	
	if (ds_map_exists(powerup_room, obj_player.targetDoor) )
	{
		var powerup = ds_map_find_value(powerup_room, obj_player.targetDoor);
		var found_time = ds_map_find_value(powerup, "poweruptime");
		
		if (found_time == pathtime.any 
		|| (global.panic && found_time== pathtime.pizzatime)
		|| (!global.panic && found_time == pathtime.notpizzatime) )
		{
			var found_type = ds_map_find_value(powerup, "poweruptype");
			rd_give_transformation(found_type);
		}
	}
}

with (obj_pause)
{
	if (variable_instance_exists(self, "roomtorestart") )
		show_debug_message( concat("Pause's Room to restart: ", roomtorestart) );
}

if (variable_global_exists("leveltorestart"))
	show_debug_message( concat("Level to restart: ", global.leveltorestart, " title: ", room_get_name(global.leveltorestart)) );