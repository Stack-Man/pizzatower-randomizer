function rd_generate_new(use_new_seed = false)
{
	rd_init(use_new_seed);

	global.sequence_tested_rooms = ds_map_create(); //Doesn't get cleared between sequences
	global.connection_tested_rooms = ds_map_create(); //Does get cleared whenever calling rd_find_connections_start
	global.connection_tested_exits = ds_list_create(); //same as above

	global.transition_map = ds_map_create();
	global.powerup_map = ds_map_create();
	global.all_rooms = rd_parse_rooms();
	
	var created = rd_construct_levels();

	ds_map_destroy(global.all_rooms);
	ds_map_destroy(global.connection_tested_rooms);
	ds_map_destroy(global.sequence_tested_rooms);
	ds_list_destroy(global.connection_tested_exits);
	
	if (variable_global_exists("font_map"))
		create_transformation_tip( concat("Generated ", created, " of ", array_length(level_names), " levels") );
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

function rd_filter_paths_by_start(from_room, desired_type, desired_dir, desired_time, desired_letter = "")
{
	//show_debug_message( concat("Filtering start paths for ", from_room.title));
	
	return rd_filter_paths(from_room, desired_type, desired_dir, desired_time, desired_letter, true);
}

function rd_filter_paths_by_start_and_roomtype(
	from_room, desired_transition_type,  desired_dir, desired_time, desired_roomtypes, desired_letter = "", use_branch_start = false, use_branch_exit = false)
{
	var unfiltered_paths = rd_filter_paths_by_start(from_room, desired_transition_type, desired_dir, desired_time, desired_letter);
	
	if (from_room.title == global.test_name)
	{
		show_debug_message( concat("unfiltered paths size for ", global.test_name, ": ", ds_list_size(unfiltered_paths) ) );
		show_debug_message( concat("Using branch start? exit? ", use_branch_start, " and  ", use_branch_exit) );
	}
	
	if ( ! array_contains(desired_roomtypes, roomtype.oneway) ) //filter out oneway paths from potentialoneway rooms
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

	//TODO: may accidentally delete existing ghostking if you go into a room with a natural ghostking from a fake ghostking
	//Try to only delete the first instance
	if (instance_exists(obj_trapghost) && current_powerup == poweruptype.ghostking )
	{
		var already_destroyed = false;
		
		with (obj_trapghost)
		{
			if (!already_destroyed)
				instance_destroy(self);
			
			already_destroyed = true;
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
		scr_switchpeppino();
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


//TODO: implement rocket
//implement ghostking and "ghostking ball"
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
	show_debug_message("barrel on");
	movespeed = hsp;
	state = states.barrel;
	image_index = 0;
}

function rd_satan()
{
	show_debug_message("satan on");
	global.noisejetpack = true;
}

//TODO: this state puts peppino in the old shotgun state at first, does not remove properly, and ends his running
function rd_shotgun()
{
	show_debug_message("shotgun on");
	shotgunAnim = true;
	//state = states.shotgun;
}

function rd_gustavo()
{
	show_debug_message("gustavo on");
	scr_switchgustavo();
}
