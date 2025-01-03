function rd_init(new_seed = false)
{
	//TODO: implement reading the ini file
	seed = 0;
	
	if (seed == 0 || new_seed)
	{
		randomize();
		seed = floor(random_range(-2147483648, 2147483647));
	}
	
	random_set_seed(seed);
}

function rd_parse_rooms()
{
	var jsons = level_names;
	
	var parsed_rooms = ds_map_create();

	for (var j = 0; j < array_length(jsons); j++)
	{
		var level = undefined;
		var directory = working_directory + "/json/" + jsons[j] + ".json"
		
		if (file_exists(directory))
		{
			var json = "";
			var file = file_text_open_read(directory);
			
			while(!file_text_eof(file))
			{
				json += file_text_readln(file);
			}
			
			file_text_close(file);
			
			level = json_decode(json);
		}
		
		if (level != undefined)
		{
			var rooms = ds_map_find_value(level, "rooms")
			
			//for (var i = 0; i < array_length(rooms); i++)
			for (var i = 0; i < ds_list_size(rooms); i++)
			{
				//var thisroom = rooms[i];
				var thisroom = ds_list_find_value(rooms, i);
				
				if (ds_map_exists(thisroom, "doors") )
				{
					var parsed_room = rd_parse_doors(thisroom);
					ds_map_add(parsed_rooms, ds_map_find_value(thisroom, "title"), parsed_room);
				}
					
			}
		}
		
	}
	
	
	show_debug_message(concat("parsed room size: ", ds_map_size(parsed_rooms)));
	
    return parsed_rooms;
}

function rd_parse_doors(thisroom)
{
	var doors  = ds_map_find_value(thisroom, "doors");   //Holds doors in the room
	
	var found_paths = ds_list_create(); //Hold the created paths

	var found_path_time = pathtime.any; //when the path is accessible
	var room_type = roomtype.twoway; //how the room can be traversed
	
	var has_pizzatime = false;	//helps determine if the room is branching
	var has_notpizzatime = false; //helps determine if the room is branching

	var door_count = ds_list_size(doors);
	
	//For every pair of transitions
	for (var i = 0; i < door_count; i++)
	{
		var start_door = ds_list_find_value(doors, i);
		
		for (var j = 0; j < door_count; j++)
		{
			var exit_door = ds_list_find_value(doors, j);
			
			//If it is not the same transition UNLESS there are no other transitions
			if (ds_map_find_value(start_door, "letter") != ds_map_find_value(exit_door, "letter") || door_count <= 1)
			{
				found_path_time = pathtime.any;
				
				//start or exit is not valid
				if (ds_map_exists(start_door, "exitonly") 
				||  ds_map_exists(exit_door, "startonly"))
					continue;
				
				//Start and exit aren't accessible at the same time (unless its a pillar room)
				if (!ds_map_exists(thisroom, "pillar")
				&& ( (ds_map_exists(start_door, "pizzatime") && ds_map_exists(exit_door, "notpizzatime"))
				|| (ds_map_exists(start_door, "notpizzatime") && ds_map_exists(exit_door, "pizzatime")) ) )
					continue;
				
				if (ds_map_exists(start_door, "pizzatime") || ds_map_exists(exit_door, "pizzatime"))
				{
					has_pizzatime = true;
					found_path_time = pathtime.pizzatime;
				}
				
				if (ds_map_exists(start_door, "notpizzatime") || ds_map_exists(exit_door, "notpizzatime"))
				{
					has_notpizzatime = true;
					found_path_time = pathtime.notpizzatime;
				}
				
				if ( (ds_map_exists(start_door, "pizzatime") || ds_map_exists(exit_door, "pizzatime"))
				&& (ds_map_exists(start_door, "notpizzatime") || ds_map_exists(exit_door, "notpizzatime")) )
				{
					found_path_time = pathtime.any;
				}
				
				//Set the room type as branching
				if (has_pizzatime && has_notpizzatime)
				{
					room_type = roomtype.branching;
					
				}
				
				if (room_type == roomtype.twoway)
				{
					if (ds_map_exists(exit_door, "exitonly"))
					{
						if (ds_map_exists(exit_door, "ratblocked"))
							room_type = roomtype.ratblockedtwoway;
						else
							room_type = roomtype.oneway;
					}
					else if (ds_map_exists(start_door, "startonly"))
					{
						if (ds_map_exists(start_door, "ratblocked"))
							room_type = roomtype.potentialratblockedtwoway;
						else
							room_type = roomtype.potentialoneway;
					}
				}
				
				var start_door_struct = {
					startonly : ds_map_exists(start_door, "startonly"),
					ratblocked : ds_map_exists(start_door, "ratblocked")
				};
				
				var exit_door_struct = {
					exitonly : ds_map_exists(exit_door, "exitonly"),
					ratblocked : ds_map_exists(exit_door, "ratblocked")
				};
				
				//add the pair of doors
				var parsed_path = {
					startletter : ds_map_find_value(start_door, "letter"),
					exitletter : ds_map_find_value(exit_door, "letter"),
					starttype : rd_convert_transitiontype(ds_map_find_value(start_door, "type")),
					exittype : rd_convert_transitiontype(ds_map_find_value(exit_door, "type")),
					startdir :  rd_convert_transitiondir(ds_map_find_value(start_door, "dir")),
					exitdir : rd_convert_transitiondir(ds_map_find_value(exit_door, "dir")),
					startdoor : start_door_struct,
					exitdoor : exit_door_struct
				};
				
				if (ds_map_exists(start_door, "powerup") )
				{
					var powerup = ds_map_find_value(start_door, "powerup");
					
					var powerup_path_time = pathtime.any;
					
					if (ds_map_exists(powerup, "pizzatime"))
						powerup_path_time = pathtime.pizzatime;
					else if (ds_map_exists(powerup, "notpizzatime") )
						powerup_path_time = pathtime.notpizzatime;
					
					var start_powerup = {
						poweruptype : ds_map_find_value(powerup, "type"),
						poweruptime : powerup_path_time
					};
					
					var room_index = asset_get_index( ds_map_find_value(thisroom, "title") );
					
					if (! ds_map_exists(global.powerup_map, room_index) )
					{
						ds_map_add(global.powerup_map, room_index, ds_map_create() );
					}
					
					ds_map_add( ds_map_find_value(global.powerup_map, room_index), ds_map_find_value(start_door, "letter"), start_powerup);
				}
				
				
				
				parsed_path.pathtime = found_path_time;
			
				ds_list_add(found_paths, parsed_path);
			}
		}
	}

	//Determine if it is also an entrance or pillar room
	if (ds_map_exists(thisroom, "entrance"))
	{
		if (room_type == roomtype.branching)
			room_type = roomtype.entrancebranching;
		else
			room_type = roomtype.entrance;
	}	
	else if (ds_map_exists(thisroom, "pillar"))
	{
		if (room_type == roomtype.branching)
			room_type = roomtype.johnbranching;
		else
			room_type = roomtype.john;

	}
	
	//determine if it should be looping
	if (door_count <= 1 && room_type != roomtype.entrance && room_type != roomtype.john)
		room_type = roomtype.loop;

	//add the type of room thsi is to the finished room object
	//Add the paths after it has been initialized
	ds_list_shuffle(found_paths);
	
	var parsed_room = {
		title : ds_map_find_value(thisroom, "title"),
		paths : found_paths,
	};
	
	parsed_room.roomtype = room_type;
	
	return parsed_room;
}