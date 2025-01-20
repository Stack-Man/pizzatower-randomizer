function rd_generate_new(use_new_seed = false)
{
	var generate = rd_init(use_new_seed);

	if (generate)
	{
		global.sequence_tested_rooms = ds_map_create(); //Doesn't get cleared between sequences
		global.connection_tested_rooms = ds_map_create(); //Does get cleared whenever calling rd_find_connections_start
		global.connection_tested_exits = ds_list_create(); //same as above
		global.sequence_used_rooms = ds_map_create();

		global.transition_map = ds_map_create();
		global.powerup_map = ds_map_create();
		global.all_rooms = rd_parse_rooms();
		
		if (!global.missing_json)
		{
			var johns = ds_list_size(rd_get_rooms_of_type([roomtype.john, roomtype.johnbranching]));
			var entrances = ds_list_size( rd_get_rooms_of_type( [roomtype.entrance, roomtype.entrancebranching] ) );
	
			show_debug_message( concat("Johns: ", johns, " entrances: ", entrances) );
	
			var created = rd_construct_levels();

			ds_map_destroy(global.sequence_used_rooms);
			ds_map_destroy(global.all_rooms);
			ds_map_destroy(global.connection_tested_rooms);
			ds_map_destroy(global.sequence_tested_rooms);
			ds_list_destroy(global.connection_tested_exits);
	
			if (variable_global_exists("font_map"))
				create_transformation_tip( concat("Generated ", created, " of ", "21", " levels") );
		
			rd_save_seed();
		}
	}

}

function rd_reset()
{
	ds_map_destroy(global.transition_map);
	ds_map_destroy(global.powerup_map);
	
	rd_generate_new(true);
}

function rd_convert_transitiondir(dir_text)
{
	switch(dir_text)
	{
		case "up":
			return transitiondir.up;
		case "down":
			return transitiondir.down;
		case "left":
			return transitiondir.left;
		case "right":
			return transitiondir.right;
		default:
			return transitiondir.none;
	}
}

function rd_convert_transitiontype(type_text)
{
	switch(type_text)
	{
		case "vertical":
			return transition.vertical;
		case "horizontal":
			return transition.horizontal;
		case "door":
			return transition.door;
		case "box":
			return transition.box;
		case "secret":
			return transition.secret;
		case "rocket":
			return transition.rocket;
		case "taxi":
			return transition.taxi;
		default:
			return transitiondir.none;
	}
}

function rd_get_opposite_dir(transition_dir)
{
	switch(transition_dir)
	{
		case transitiondir.up:
			return transitiondir.down;
		case transitiondir.left:
			return transitiondir.right;
		case transitiondir.right:
			return transitiondir.left;
		case transitiondir.down:
			return transitiondir.up;
		default:
			return transitiondir.none;
	}
}

function rd_check_type(thisroom, type)
{
	return thisroom.roomtype == type;
}

function rd_list_contains_exit(list, exitpair)
{
	for (var i = 0; i < ds_list_size(list); i++)
	{
		var listpair = ds_list_find_value(list, i);
		
		if (exitpair.exittype == listpair.exittype && exitpair.exitdir == listpair.exitdir)
			return true;
	}
	
	return false;
}

function rd_remove_room(thisroom)
{
	if (ds_map_exists(global.all_rooms,  thisroom.title ) )
		ds_map_delete(global.all_rooms,  thisroom.title );
}

function rd_filter_out_rooms(potential_rooms, rooms_to_remove)
{
	var valid_rooms = ds_list_create();
	
	for (var i = 0; i < ds_list_size(potential_rooms); i++)
	{
		var thisroom = ds_list_find_value(potential_rooms, i);
		
		if (! ds_map_exists(rooms_to_remove, thisroom.title ) )
			ds_list_add(valid_rooms, thisroom);
	}
	
	return valid_rooms;
}

function rd_prioritize_rooms_of_type(potential_rooms, roomorder)
{
	var result_rooms = ds_list_create();
	
	for (var r = 0; r < array_length(roomorder); r++)
	{
		var current_roomtype = roomorder[r];
		
		for (var p = 0; p < ds_list_size(potential_rooms); p++)
		{
			var thisroom = ds_list_find_value(potential_rooms, p);
			
			if (thisroom.roomtype == current_roomtype)
				ds_list_add(result_rooms, thisroom);
			
		}
	}
	
	for (var p = 0; p < ds_list_size(potential_rooms); p++)
	{
		var thisroom = ds_list_find_value(potential_rooms, p);
			
		if ( !rd_array_contains(roomorder, thisroom.roomtype) )
			ds_list_add(result_rooms, thisroom);
			
	}
	
	/*show_debug_message("Prioritized rooms: ");
	
	for (var p = 0; p < ds_list_size(result_rooms); p++)
	{
		var thisroom = ds_list_find_value(result_rooms, p);
			
		show_debug_message(concat("Room of type ", thisroom.roomtype, ": ", thisroom.title));
			
	}*/
	
	return result_rooms;
	
}

function rd_filter_paths_by_start(from_room, desired_type, desired_dir, desired_time, desired_letter = "")
{
	//show_debug_message( concat("Filtering start paths for ", from_room.title));
	
	return rd_filter_paths(from_room, desired_type, desired_dir, desired_time, desired_letter, true);
}

function rd_filter_paths_by_start_and_roomtype(
	from_room, desired_transition_type,  desired_dir, desired_time, desired_roomtypes, desired_letter = "", use_branch_start = false, use_branch_exit = false)
{
	var unfiltered_paths = rd_filter_paths_by_start(from_room, desired_transition_type, desired_dir, desired_time, desired_letter);
	
	if (from_room.title == global.first_test_name  || global.print_connection_debug)
	{
		show_debug_message( concat("unfiltered paths size for ", from_room.title, ": ", ds_list_size(unfiltered_paths) ) );
		show_debug_message( concat("Using branch start? exit? ", use_branch_start, " and  ", use_branch_exit) );
	}
	
	if ( ! rd_array_contains(desired_roomtypes, roomtype.oneway) ) //filter out oneway paths from potentialoneway rooms
	{
	
		var filtered_paths = ds_list_create();
	
		for (var i = 0; i < ds_list_size(unfiltered_paths); i++)
		{
			var path = ds_list_find_value(unfiltered_paths, i);
			
			//The path is oneway, unless it is also ratblocked
			//unless startdoor is branch and we use start branch
			//unless exitdoor is branch and we use exit branch
			var good_branch = (path.startdoor.branch && use_branch_start) || (path.exitdoor.branch && use_branch_exit);
			
			//It doesnt matter which is startonly/exitonly if either of them is a branch and we are using it
			var bad_start = (path.startdoor.startonly && !path.startdoor.ratblocked );
			var bad_exit = (path.exitdoor.exitonly && !path.exitdoor.ratblocked);
			
			if ( (bad_start || bad_exit) && !good_branch )
			{
				if (from_room.title == global.test_name)
				{
					show_debug_message( concat("bad oneway path for ", global.test_name, path ) );
				}
			}
			else
			{
				ds_list_add(filtered_paths, path);
				if (from_room.title == global.test_name)
				{
					show_debug_message( concat("good not oneway path for ", global.test_name, path ) );
				}
			}
		}

		ds_list_destroy(unfiltered_paths);
	
		return filtered_paths;
	}
	
	return unfiltered_paths;
}

function rd_filter_paths_by_exit(from_room, desired_type, desired_dir, desired_time, desired_letter = "")
{
	return rd_filter_paths(from_room, desired_type, desired_dir, desired_time, desired_letter, false);
}

function rd_get_last_path(connection)
{
	var next = connection;
	
	while (next != undefined)
	{
		if (next.second == undefined) //last room
			return next.path;
		
		next = next.second;
	}
	
	return undefined;
}

function rd_print_connection_path(connection)
{
	var next = connection;
	
	var path = "";
	
	while (next != undefined)
	{
		path = concat(path, " -> ", next.first.title, " ", next.path.startdoor.letter, " to ", next.path.exitdoor.letter);
		
		next = next.second;
	}
	
	show_debug_message( concat("Path: ", path) );
}

function rd_count_rooms(sequence)
{
	var next = sequence;
	var total = 0;
	
	while (next != undefined)
	{
		total += rd_count_connections(next.to_connection);
		total += rd_count_connections(next.return_connection);
		
		next = next.next;
	}
	
	return total;
}

function rd_count_connections(connection)
{
	var next = connection;
	var total = 0;
	
	while (next != undefined)
	{
		total++;
		next = next.second;
	}
	
	return total;
}

function rd_add_connection_to_end_replace(connection, connection_to_add)
{
	var next = connection;
	var last = undefined;
	
	while (next != undefined)
	{
		last = next;
		next = next.second;
	}
	
	//last.first = connection_to_add.first; //probably redundant!
	last.second = connection_to_add.second;
	//last.path = connection_to_add.path; //don't replace the path because we found a new path to use, the original path is not valid
}

function rd_add_sequence_rooms_to_map(sequence, map)
{
	var next = sequence;
	
	while (next != undefined)
	{
		//will automatically end if either is undefined
		rd_add_connection_rooms_to_map(next.to_connection, map);
		rd_add_connection_rooms_to_map(next.return_connection, map);
		
		next = next.next;
	}
}

function rd_add_connection_rooms_to_map(connection, map)
{
	var next = connection;
	
	while (next != undefined)
	{
		ds_map_add(map, next.first.title, next.first);
		next = next.second;
	}
}

function rd_remove_connection_rooms_from_map(connection, map)
{
	var next = connection;
	
	while (next != undefined)
	{
		ds_map_delete(map, next.first.title);
		next = next.second;
	}
}

function rd_get_door_struct(door)
{
	var door_struct =
	{
		startonly : ds_map_exists(door, "startonly"),
		exitonly : ds_map_exists(door, "exitonly"),
		branch : ds_map_exists(door, "branch"),
		branchstart : ds_map_exists(door, "branchstart"),
		branchexit : ds_map_exists(door, "branchexit"),
		ratblocked : ds_map_exists(door, "ratblocked"),
			
		pizzatime : ds_map_exists(door, "pizzatime"),
		notpizzatime : ds_map_exists(door, "notpizzatime"),
		
		letter : ds_map_find_value(door, "letter"),
		type : rd_convert_transitiontype(ds_map_find_value(door, "type")),
		dir : rd_convert_transitiondir(ds_map_find_value(door, "dir"))
		
	};
	
	return door_struct;
}

function rd_get_exit_struct(path)
{
	var exitpair = 
	{
		exittype : path.exitdoor.type,
		exitdir : path.exitdoor.dir
	};
			
	return exitpair;
}

function rd_get_sequence_struct(new_to_connection, new_return_connection, new_next, new_last_room, new_is_end_branch)
{
	var new_sequence = 
		{
			to_connection : new_to_connection,
			return_connection : new_return_connection,
			next : new_next,
			last_room : new_last_room,
			last_room_is_end_branch : new_is_end_branch
		};
		
	return new_sequence;
}

function rd_get_connection_struct(new_first, new_path, new_second)
{
	var new_connection =
	{
		first: new_first,
		path: new_path,
		second: new_second
	};
	
	return new_connection;
}

function rd_clear_transformation()
{
	if (instance_exists(obj_wartimer))
	{
		with(obj_wartimer)
		{
			instance_destroy(self);
		}
	}

	if (instance_exists(obj_trapghost))
	{
		with (obj_trapghost)
		{
			instance_destroy(self);
		}
	}

	if (current_powerup == poweruptype.satan)
	{
		global.noisejetpack = false;
	}
	
	//Clear any powerups leftover (mort barrel rocket?)
	with (obj_player)
	{
		//TODO: will this prevent clearing transformations upon exiting a door? This function gets called 2 frames after entering the room so maybe not
		if (!scr_transformationcheck() && state != states.comingoutdoor && state != states.door)
		{
			if state == states.ghost
				notification_push(notifs.priest_ghost, [ghosttimer, room]);
			if (state == states.mort || state == states.mortjump || state == states.morthook || state == states.mortattack || state == states.mortjump || state == states.boxxedpep || state == states.boxxedpepjump || state == states.boxxedpepspin || state == states.ghost || state == states.barrelslide || state == states.barrel || state == states.barreljump)
			{
				if hsp != 0
					xscale = sign(hsp);
				movespeed = abs(hsp);
			}

			transformationsnd = false;
			state = states.normal;
			sprite_index = spr_idle;
			dir = xscale;
			ghostdash = false;
			ghostpepper = 0;
		}
	}
	
	//Clear natural and given shotgun
	//TODO: clear war flashing red background
	with (obj_player)
	{
		if shotgunAnim
		{
			shotgunAnim = false;

			if state == states.shotgunshoot
				state = states.normal;
		}
	
	}
	
	if (current_powerup == poweruptype.gustavo)
	{
		rd_peppino();
	}

	current_powerup = poweruptype.none;
}

function rd_buffer()
{
	var buffer = "";
	
	for (var i = 0; i < global.recursion_depth; i++)
	{
		buffer = concat(buffer, " ");
	}
	
	return buffer;
}

//TODO: implement "ghostking ball" for that gerome door loop room in chateau
function rd_give_transformation(name)
{
	show_debug_message( concat("Giving Powerup: ", name) );
	
	with (obj_player)
	{
		switch (name)
		{
			case "barrel":
				rd_barrel();
				break;
			case "satan":
				rd_satan();
				break;
			case "shotgun":
				rd_shotgun();
				break;
			case "gustavo":
				rd_gustavo();
				break;
			case "ghostking":
				rd_ghostking();
				break;
			case "rocket":
				rd_rocket();
				break;
			default:
				break;
		}
	}
	
	switch (name)
	{
		case "barrel":
			current_powerup = poweruptype.barrel;
			break;
		case "satan":
			current_powerup = poweruptype.satan;
			break;
		case "shotgun":
			current_powerup = poweruptype.shotgun;
			break;
		case "gustavo":
			current_powerup = poweruptype.gustavo;
			break;
		case "ghostking":
			current_powerup = poweruptype.ghostking;
		default:
			break;
	}
	
}

function rd_rocket()
{
	with (obj_player)
	{
		state = states.rocket;
		sprite_index = spr_rocketstart;
		image_index = 0;
		if movespeed < 8
			movespeed = 8;
	}
}

function rd_ghostking()
{
	if (!instance_exists(obj_trapghost) )
	{
		with(obj_player)
		{
			instance_create_depth(x, y, depth, obj_trapghost);
		}
	}
}

function rd_barrel()
{
	movespeed = hsp;
	state = states.barrel;
	image_index = 0;
}

function rd_satan()
{
	global.noisejetpack = true;
}

function rd_shotgun()
{
	shotgunAnim = true;
}

function rd_peppino()
{
	with obj_player1
	{
		if isgustavo
		{
			isgustavo = false;
			brick = false;

			sprite_index = spr_player_idle;
			
			var in_mach_speed = gustavodash == 51;
			gustavodash = 0;
			
			switch (state)
			{
				case states.comingoutdoor:
					state = states.comingoutdoor;
					break;
				case 191: //rat idle
					if (in_mach_speed)
					{
						state = 121;
						sprite_index = spr_player_mach4;
					}
					else
						state = 104;
					break;
				case 192: //rat jump
					if (in_mach_speed)
					{
						state = 121;
						sprite_index = spr_player_mach4;
					}
					else
						state = 92;
					break;
				case 259: //gustavo spin
					state = 42;
					break;
				//case 204: //skid
					//state = 105;
					//break;
				case 197: //stomp
					state = 108;
					break;
				default:
					state = states.normal;
					break;
			}
			
			if (movespeed < 0) //flip to positive if it was negative (its can be negative as gus)
				movespeed = movespeed * -1;
		}
		
	}
	
	with obj_swapmodefollow
	{
		isgustavo = false;
		get_character_spr();
	}
}

function rd_gustavo()
{
	with obj_player1
	{
		if ispeppino
		{
			//gustavodash = 0;
			isgustavo = true;
			
			sprite_index = spr_player_ratmountidle;

			brick = true;
			
			switch (state)
			{	
				case 5: //grabslide
					state = states.ratmount;
					//gustavodash = 51;
					sprite_index = spr_player_ratmountmach3;
					
					break;
				
				case 121: //run
					state = states.ratmount;
					//gustavodash = 51;
					sprite_index = spr_player_ratmountmach3;
					
					break;
				case 108: //groundpound
					state = 197;
					break;
				case states.comingoutdoor:
					state = states.comingoutdoor;
					break;
				default:
					state = states.ratmount;
					break;
			}
			
			if (hsp < 0) //make negative for gus, since its only positive as peppino
				movespeed = hsp;
			
			ratmount_movespeed = min(12, abs(movespeed) );
			
			if (abs(movespeed) >= 12)
				gustavodash = 51;
			
			if (movespeed > 12)
				movespeed = 12;
			
			if (movespeed < -12)
				movespeed = -12;
			
			if (hsp > 12)
				hsp = 12;
			
			if (hsp < -12)
				hsp = -12;
		}
	}
	with obj_swapmodefollow
	{
		isgustavo = true;
		get_character_spr();
	}
}

function rd_check_levels_beat()
{
	ini_open_from_string(obj_savesystem.ini_str);
	
	global.total_levels = 4;
	
	if (room == tower_1 || room == tower_johngutterhall || room == tower_entrancehall)
	{
		rd_check_levels(["entrance", "ruin", "dungeon", "medieval"]);
	}
	else if (room == tower_2)
	{
		rd_check_levels(["saloon", "farm", "badland", "graveyard"]);
	}
	else if (room == tower_3)
	{
		rd_check_levels(["space", "minigolf", "plage", "forest"]);
	}
	else if (room == tower_4)
	{
		rd_check_levels(["freezer", "industrial", "sewer", "street"]);
	}
	else if (room == tower_5 || room == tower_pizzafacehall || room == tower_outside)
	{
		global.total_levels = 3;
		rd_check_levels(["war", "kidsparty", "chateau"]);
	}	
		
	ini_close();
}

function rd_check_levels(level_names)
{
	var beat_all = true;
	var beat_total = 0;
	
	for (var l = 0; l < array_length(level_names); l++)
	{
		var highscore = ini_read_real("Highscore", level_names[l], -1);
		
		if (highscore == -1)
			beat_all = false;
		else
			beat_total++;
		
	}
	
	global.beat_all_levels = beat_all;
	global.levels_beat = beat_total;
}

function rd_send_to_door(door_object)
{
	if (instance_exists(door_object))
	{
		global.door_x = door_object.x;
		
		if hallway == 1
		{
			var true_direction = 0;
			
			if (place_meeting(door_object.x, door_object.y, obj_hallway) )
			{
				with ( instance_place(door_object.x, door_object.y, obj_hallway) )
				{
					true_direction = image_xscale * -1;
				}
			}
			
			global.true_direction = true_direction;
			
			x = door_object.x + (true_direction * 100);
		}	
		else if box == 1
		{
			x = door_object.x + 32;
		}
		else
		{
			x = door_object.x + 16;
		}
		
		global.door_x_offset = x - global.door_x;
			
		y = door_object.y - 14;
		
		global.door_y = door_object.y;
		
	}
}