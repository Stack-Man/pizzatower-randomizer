function rd_init(use_new_seed = false)
{
	//TODO: implement reading the ini file
	seed = 422622450;
	
	if (seed == 0 || use_new_seed)
	{
		randomize();
		seed = floor(random_range(-2147483648, 2147483647));
	}
	
	show_debug_message( concat("Seed: ", seed) );
	
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
		show_debug_message( concat("Parsing Level: ", directory ) );
		
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
			
			for (var i = 0; i < ds_list_size(rooms); i++)
			{
				//var thisroom = rooms[i];
				var thisroom = ds_list_find_value(rooms, i);
				
				if (ds_map_exists(thisroom, "doors"))
				{
					if (array_contains(ignore_rooms, ds_map_find_value(thisroom, "title")) ) //skip this room
						continue;
					
					var parsed_room = rd_parse_doors(thisroom);
					var room_title = ds_map_find_value(thisroom, "title");
					
					if (ds_map_exists(parsed_rooms, room_title) )
					{
						var temp = room_title;
						
						room_title = concat(room_title, "_SECOND");
						
						if (ds_map_exists(parsed_rooms, room_title) )
						{
							room_title = concat(temp, "_THIRD_"); //making it seven characters long like _SECOND
						}
					}
					
					ds_map_add(parsed_rooms, ds_map_find_value(thisroom, "title"), parsed_room);
				}
					
			}
		}
		
	}
	
	
	show_debug_message(concat("parsed room size: ", ds_map_size(parsed_rooms)));
	
    return parsed_rooms;
}

//TODO: change to check all paths at once
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

function rd_check_paths_for_branchtype(path_ab, path_ba, current_type)
{
	if ((path_ab != undefined && !path_ab.startdoor.branch && !path_ab.exitdoor.branch)
	||  (path_ba != undefined && !path_ba.startdoor.branch && !path_ba.exitdoor.branch))
		return current_type; //branch check failed
	
	//path == undefined means the other is a oneway
	//to branch path (ba) being oneway is a valid alternative to being notpizzatime/pizzatime exclusive
	
	var branch_NPT = (path_ab != undefined) && path_ab.startdoor.branch && path_ab.pathtime == pathtime.notpizzatime;
	var NPT_branch = (path_ba != undefined) && (path_ba.pathtime == pathtime.notpizzatime || path_ba.oneway) && path_ba.exitdoor.branch;
	
	var branch_PT = (path_ab != undefined) && path_ab.startdoor.branch && path_ab.pathtime == pathtime.pizzatime;
	var PT_branch = (path_ba != undefined) && (path_ba.pathtime == pathtime.pizzatime || path_ba.oneway) && path_ba.exitdoor.branch;
	
	if ( (branch_NPT && ! NPT_branch) || (branch_PT && ! PT_branch) )
		return roomtype.branchstart;
	
	if ( (NPT_branch && ! branch_NPT) || (PT_branch && ! branch_PT) )
		return roomtype.branchend;
	
	if ( (branch_NPT && NPT_branch) || (branch_PT && PT_branch) )
		return roomtype.branchany;
	
	return current_type; //branch check failed
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
	if (start_door.exitonly || exit_door.startonly)
		return undefined;
	
	if (!has_pillar && ((start_door.pizzatime && exit_door.notpizzatime) || (start_door.notpizzatime && exit_door.pizzatime)) )
		return undefined;
		
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
					
		var start_powerup = {
			poweruptype : ds_map_find_value(powerup, "type"),
			poweruptime : powerup_path_time
		};
							
		if (! ds_map_exists(global.powerup_map, room_index) )
			ds_map_add(global.powerup_map, room_index, ds_map_create() );
					
		ds_map_add( ds_map_find_value(global.powerup_map, room_index), ds_map_find_value(door, "letter"), start_powerup);
	}
}

function rd_parse_doors(thisroom)
{
	show_debug_message( concat("Parsing: ", ds_map_find_value(thisroom, "title") ) );
	
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
			
			//TODO: loop rooms add two identical paths
			
			if (path_ab != undefined)
				ds_list_add(found_paths, path_ab);
			
			if (path_ba != undefined)
				ds_list_add(found_paths, path_ba);
		}
	}
	
	//Check for john, entrance, branch variant, or branchmid
	found_room_type = rd_check_all_paths_for_special_branch(found_paths, has_pillar, has_entrance, found_room_type);
	
	if (found_room_type == roomtype.john || found_room_type == roomtype.entrance)
		show_debug_message( concat(room_title, " is john or entrance ") );
	
	if (found_room_type == roomtype.johnbranching || found_room_type == roomtype.entrancebranching)
		show_debug_message( concat(room_title, " is john branching or entrance branching") );

	if (ds_list_size(filtered_doors) <= 1 && found_room_type != roomtype.entrance && found_room_type != roomtype.john)
		found_room_type = roomtype.loop;

	if (room_title == "war_13")
		found_room_type = roomtype.warexit;

	ds_list_destroy(filtered_doors);

	//seeded shuffling of paths
	ds_list_shuffle(found_paths);
	
	var parsed_room = {
		title : room_title,
		paths : found_paths,
		roomtype : found_room_type
	};
	
	return parsed_room;
}