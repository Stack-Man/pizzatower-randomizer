rd_clear_transformation();
			
if (ds_map_exists(global.powerup_map, room) )
{
	var powerup_room = ds_map_find_value(global.powerup_map, room);
	
	if (ds_map_exists(powerup_room, obj_player.targetDoor) )
	{
		var powerup = ds_map_find_value(powerup_room, obj_player.targetDoor);
		
		if (powerup.poweruptime == pathtime.any 
		|| (global.panic && powerup.poweruptime == pathtime.pizzatime)
		|| (!global.panic && powerup.poweruptime == pathtime.notpizzatime) )
		{
			rd_give_transformation(powerup.poweruptype); //TODO: not implemented
		}
	}
}