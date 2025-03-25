function rd_init(use_new_seed = false)
{
	seed = 0;
	
	if (override_seed != 0)
	{
		seed = override_seed;
		rd_add_to_log("override seed used");
		random_set_seed(seed);
		return true;
	}
	
	
	if (!use_new_seed)
	{
		rd_create_or_read_ini();
	
		var directory = concat("randomizer/main.json");

		var should_load_json = false;
		
		if (file_exists(directory))
		{
			should_load_json = true;
		}
		else if (seed != 0)
		{
			should_load_json = true;
			directory = concat("randomizer/", seed, ".json");
		}

		if (should_load_json)
		{
			rd_add_to_log(concat("Loading seed ", directory) );
			
			var final_map = undefined;
			
			if (file_exists(directory))
			{
				var json = "";
				var file = file_text_open_read(directory);
			
				while(!file_text_eof(file))
				{
					json += file_text_readln(file);
				}
			
				file_text_close(file);
			
				final_map = json_decode(json);
			}
			
			if (final_map != undefined)
			{
				global.transition_map = ds_map_create();
				global.powerup_map = ds_map_create();
				
				//replace the stringified room index keys with numbers again
				var temp_transition_map = ds_map_find_value(final_map, "transitions");	
				var trans_keys_arr = []
				ds_map_keys_to_array(temp_transition_map, trans_keys_arr);
				
				for (var k = 0; k < array_length(trans_keys_arr); k++)
				{
					var letters_map = ds_map_find_value(temp_transition_map, trans_keys_arr[k]);
					var room_id = real(trans_keys_arr[k]);
					
					ds_map_add_map(global.transition_map, room_id, letters_map);
				}
				
				//replace the stringified room index keys with numbers again
				var temp_powerup_map = ds_map_find_value(final_map, "powerups");
				var powerup_keys_arr = []
				ds_map_keys_to_array(temp_powerup_map, powerup_keys_arr);
				
				for (var p = 0; p < array_length(powerup_keys_arr); p++)
				{
					var letters_map = ds_map_find_value(temp_powerup_map, powerup_keys_arr[p]);
					var room_id = real(powerup_keys_arr[p]);
					
					ds_map_add_map(global.powerup_map, room_id, letters_map);
				}
				
				seed = ds_map_find_value(final_map, "seed");
				
				var found_version = ds_map_find_value(final_map, "version");
				validversion = found_version == version;
				
				loadedjson = true;	
				
				return false; //don't generate levels
			}

		}
	
		loadedjson = false;
	}
	
	if (seed == 0 || use_new_seed)
	{
		randomize();
		seed = floor(random_range(-2147483648, 2147483647));
	}
	
	rd_add_to_log( concat("Seed: ", seed) );
	
	random_set_seed(seed);
	
	return true;
}

function rd_create_or_read_ini()
{
	var directory = concat("randomizer/randomizer.ini");
	
	ini_open(directory);
	
	if (file_exists(directory))
	{
		seed = ini_read_real("settings", "seed", 0);
		loadedini = true;
	}
	else
	{
		ini_write_real("settings", "seed", 0);
		loadedini = false;
	}
	
	ini_close();
}

function rd_save_seed()
{
	var final_map = ds_map_create();
	
	ds_map_add(final_map, "version", version);
	ds_map_add(final_map, "seed", seed);
	ds_map_add_map(final_map, "transitions", global.transition_map);
	ds_map_add_map(final_map, "powerups", global.powerup_map);

	
	var directory = concat("randomizer/", seed, ".json");
	var json = json_encode(final_map);
	
	rd_add_to_log( concat("Saving seed ", seed, " to ", directory) );
	rd_save_to_json(json, directory);
}

function rd_save_to_json(_string, _filename)
{
	var _buffer = buffer_create(string_byte_length(_string) + 1, buffer_fixed, 1);
	buffer_write(_buffer, buffer_string, _string);
	buffer_save(_buffer, _filename);
	buffer_delete(_buffer);
}

function rd_parse_rooms()
{
	var jsons = level_names;
	var parsed_rooms = ds_map_create();

	for (var j = 0; j < array_length(jsons); j++)
	{
		var level = undefined;
		var directory = concat(working_directory, "/json/", jsons[j], ".json");
		rd_add_to_log( concat("Parsing Level: ", directory ) );
		
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
		else
		{
			global.missing_json++;
		}
		
		if (level != undefined)
		{
			var this_version = "0";
			
			if (ds_map_exists(level, "version"))
			{
				this_version = ds_map_find_value(level, "version");
				
				if (this_version != version)
					global.outdated_json = true;
			}
			
			var rooms = ds_map_find_value(level, "rooms")
			
			for (var i = 0; i < ds_list_size(rooms); i++)
			{
				var thisroom = ds_list_find_value(rooms, i);
				
				if (ds_map_exists(thisroom, "doors"))
				{
					if (rd_array_contains(ignore_rooms, ds_map_find_value(thisroom, "title")) ) //skip this room
						continue;
					
					var parsed_room = rd_parse_doors(thisroom);
					var room_title = ds_map_find_value(thisroom, "title");
					
					ds_map_add(parsed_rooms, ds_map_find_value(thisroom, "title"), parsed_room);
				}
					
			}
		}
		
	}
	
	rd_add_to_log(concat("parsed room size: ", ds_map_size(parsed_rooms)));
	
    return parsed_rooms;
}

function rd_check_path_for_roomtype(path, current_type)
{
	if (path == undefined)
		return current_type; //path check failed
		
	if (ds_map_exists(path.exitdoor, "exitonly"))
	{
		if (ds_map_exists(path.exitdoor, "ratblocked"))
			return roomtype.ratblockedtwoway;
		else
			return roomtype.oneway;
	}
	else if (ds_map_exists(path.startdoor, "startonly"))
	{
		if (ds_map_exists(path.startdoor, "ratblocked"))
			return roomtype.potentialratblockedtwoway;
		else
			return roomtype.potentialoneway;
	}
	
	return current_type;
}

//Doesnt get called if the branch type is already branchstart or branchend
//maybe change because that means it never checks both pt and npt to ensure the other is valid
function rd_check_paths_for_branchtype(path_ab, path_ba, current_type)
{	
	if ((path_ab != undefined && !path_ab.startdoor.branch && !path_ab.exitdoor.branch)
	||  (path_ba != undefined && !path_ba.startdoor.branch && !path_ba.exitdoor.branch))
	{
		return current_type; //branch check failed
	}
	
	//path == undefined means the other is a oneway
	//to branch path (ba) being oneway is a valid alternative to being notpizzatime/pizzatime exclusive
	
	//Check both in case branch is a or b
	var branch_NPT = rd_branch_NPT(path_ab) || rd_branch_NPT(path_ba);
	var NPT_branch = rd_NPT_branch(path_ab) || rd_NPT_branch(path_ba);
	
	var branch_PT = rd_branch_PT(path_ab) || rd_branch_PT(path_ba);
	var PT_branch = rd_PT_branch(path_ab) || rd_PT_branch(path_ba);
	
	if ( (branch_NPT && ! NPT_branch) || (!branch_PT && PT_branch) )
		return roomtype.branchstart;
	
	if ( (NPT_branch && ! branch_NPT) || (!PT_branch && branch_PT) )
		return roomtype.branchend;
	
	if ( (branch_NPT && NPT_branch) || (branch_PT && PT_branch) )
		return roomtype.branchany;
	
	return current_type; //branch check failed
}

function rd_branch_NPT(path)
{
	return (path != undefined) && path.startdoor.branch && path.pathtime == pathtime.notpizzatime;
}

function rd_NPT_branch(path)
{
	return (path != undefined) && (path.pathtime == pathtime.notpizzatime || path.oneway) && path.pathtime != pathtime.pizzatime && path.exitdoor.branch;
}

function rd_branch_PT(path)
{
	return (path != undefined) && path.startdoor.branch && path.pathtime == pathtime.pizzatime;
}

function rd_PT_branch(path)
{
	return (path != undefined) && (path.pathtime == pathtime.pizzatime || path.oneway) && path.pathtime != pathtime.notpizzatime  && path.exitdoor.branch;
}


function rd_check_all_paths_for_special_branch(paths, has_pillar, has_entrance, current_type)
{
	var has_pizzatime = false;
	var has_notpizzatime = false;
	
	var has_branchstart = false;
	
	for (var p = 0; p < ds_list_size(paths); p++)
	{
		var path = ds_list_find_value(paths, p);
		
		//TODO: may be redundant with the below check
		if (path.pathtime == pathtime.pizzatime)
			has_pizzatime = true;
		else if (path.pathtime == pathtime.notpizzatime)
			has_notpizzatime = true;
		
		//Accounts for john branching paths as well which are marked as pathtime.any
		if (path.startdoor.pizzatime || path.exitdoor.pizzatime)
			has_pizzatime = true;
		
		if (path.startdoor.notpizzatime || path.exitdoor.notpizzatime)
			has_notpizzatime = true;
		
		if (has_pizzatime && has_notpizzatime)
		{
			if (has_pillar)
				return roomtype.johnbranching;
				
			if (has_entrance)
				return roomtype.entrancebranching;
		}
		
		if (path.startdoor.branchstart)
			return roomtype.branchmid;
	}
	
	if (has_pillar)
		return roomtype.john;
	
	if (has_entrance)
		return roomtype.entrance;
	
	return current_type; //check failed
}


function rd_parse_path(start_door, exit_door, has_pillar)
{
	rd_add_to_log( concat("Parsing ", start_door.letter, " to ", exit_door.letter) );
	
	if (start_door.exitonly || exit_door.startonly)
	{
		rd_add_to_log( concat("Above failed due to start door exitonly or exit door startonly") );
		return undefined;
	}
	
	if (start_door.notpizzatimeexitonly && (start_door.notpizzatime || exit_door.notpizzatime))
	{
		rd_add_to_log( concat("Above failed due to start being a notpizzatimeexitonly and the path being notpizzatime") );
		return undefined;
	}
	
	if (!has_pillar && ((start_door.pizzatime && exit_door.notpizzatime) || (start_door.notpizzatime && exit_door.pizzatime)) )
	{	
		rd_add_to_log( concat("Above failed due to mismatching times and not a pillar room") );
		return undefined;
	}
		
	var found_pathtime = pathtime.any;
	
	if (!has_pillar)
	{
		if (start_door.pizzatime || exit_door.pizzatime)
			found_pathtime = pathtime.pizzatime;
		
		if (start_door.notpizzatime || exit_door.notpizzatime)
			found_pathtime = pathtime.notpizzatime;
	}
	
	var found_oneway = (start_door.startonly && !start_door.ratblocked) || (exit_door.exitonly && !exit_door.ratblocked);
	var found_loop = ds_map_exists(start_door, "loop") || ds_map_exists(exit_door, "loop");
	
	var parsed_path = 
	{
		startdoor : start_door,
		exitdoor : exit_door,
		oneway : found_oneway,
		loop : found_loop,
		pathtime : found_pathtime
	};
	
	return parsed_path;
	
}

function rd_parse_powerup(door, room_index)
{
	if (ds_map_exists(door, "powerup") )
	{
		var powerup = ds_map_find_value(door, "powerup");	
		var powerup_path_time = pathtime.any;
					
		if (ds_map_exists(powerup, "pizzatime"))
			powerup_path_time = pathtime.pizzatime;
		else if (ds_map_exists(powerup, "notpizzatime") )
			powerup_path_time = pathtime.notpizzatime;
					
		var start_powerup = ds_map_create();
		ds_map_add(start_powerup, "poweruptype", ds_map_find_value(powerup, "type"));
		ds_map_add(start_powerup, "poweruptime", powerup_path_time);
							
		if (! ds_map_exists(global.powerup_map, room_index) )
			ds_map_add_map(global.powerup_map, room_index, ds_map_create() );
					
		ds_map_add_map( ds_map_find_value(global.powerup_map, room_index), ds_map_find_value(door, "letter"), start_powerup);
	}
}

function rd_parse_doors(thisroom)
{
	rd_add_to_log( concat("Parsing: ", ds_map_find_value(thisroom, "title") ) );
	
	var doors  = ds_map_find_value(thisroom, "doors"); //Holds doors in the room, don't prematurely delete, it will get delted with parsed_level later
	var filtered_doors;

	if (global.use_loops)
	{
		filtered_doors = doors;
	}
	else
	{
		filtered_doors = ds_list_create();
		
		//Filter out loops if we don't use them
		for (var d = 0; d < ds_list_size(doors); d++)
		{
			var door = ds_list_find_value(doors, d);
		
			if (ds_map_exists(door, "loop") )
				continue;
		
			ds_list_add(filtered_doors, door);
		}
	}
	
	var found_paths = ds_list_create(); //Hold the created paths

	var found_room_type = roomtype.twoway; //how the room can be traversed
	
	var has_pillar = ds_map_find_value(thisroom, "pillar");
	var has_entrance = ds_map_find_value(thisroom, "entrance");
	var room_title = ds_map_find_value(thisroom, "title");
	var room_index = asset_get_index(room_title);
	
	//For every letter
	for (var a = 0; a < ds_list_size(filtered_doors); a++)
	{
		var door_a = ds_list_find_value(filtered_doors, a);
		var door_a_struct = rd_get_door_struct(door_a);

		rd_parse_powerup(door_a, room_index);
		
		var c = (ds_list_size(filtered_doors) <= 1) ? a : a + 1; //Handle one door rooms
		
		//For every letter after that
		for (var b = c; b < ds_list_size(filtered_doors); b++)
		{
			var door_b = ds_list_find_value(filtered_doors, b);
			var door_b_struct = rd_get_door_struct(door_b);
			
			//do A start B end
			var path_ab = rd_parse_path(door_a_struct, door_b_struct, has_pillar);
			
			//do B start A end
			var path_ba = rd_parse_path(door_b_struct, door_a_struct, has_pillar);
			
			//may have yet to check a branch path, or a branchany that may be more restrictive due to PT/NPT branch path
			if (found_room_type != roomtype.branchstart && found_room_type != roomtype.branchend)
				found_room_type = rd_check_paths_for_branchtype(path_ab, path_ba, found_room_type);
			
			if (found_room_type != roomtype.branchstart && found_room_type != roomtype.branchend && found_room_type != roomtype.branchany &&
				found_room_type != roomtype.oneway && found_room_type != roomtype.potentialoneway)
			{
				found_room_type = rd_check_path_for_roomtype(path_ab, found_room_type);
				found_room_type = rd_check_path_for_roomtype(path_ba, found_room_type);
			}
			
			if (path_ab != undefined)
				ds_list_add(found_paths, path_ab);
			
			if (path_ba != undefined && door_a_struct.letter != door_b_struct.letter) //add only one in case of loop paths
				ds_list_add(found_paths, path_ba);
		}
	}
	
	//Check for john, entrance, branch variant, or branchmid
	found_room_type = rd_check_all_paths_for_special_branch(found_paths, has_pillar, has_entrance, found_room_type);

	if (ds_list_size(filtered_doors) <= 1 && found_room_type != roomtype.entrance && found_room_type != roomtype.john)
		found_room_type = roomtype.loop;

	if (room_title == "war_13")
		found_room_type = roomtype.warexit;
	
	if (room_title == "tower_entrancehall")
		found_room_type = roomtype.ctopexit;
	
	if (room_title == "tower_finalhallway")
		found_room_type = roomtype.ctopentrance;

	ds_list_destroy(filtered_doors);

	//seeded shuffling of paths
	ds_list_shuffle(found_paths);
	
	var parsed_room = {
		title : room_title,
		paths : found_paths,
		roomtype : found_room_type
	};
	
	rd_add_to_log( concat("Parsed: ", ds_map_find_value(thisroom, "title"), " type: ", found_room_type ) );
	
	return parsed_room;
}