function rd_generate_new(use_new_seed = false)
{
	rd_init(use_new_seed);

	global.sequence_tested_rooms = ds_map_create(); //Doesn't get cleared between sequences
	global.connection_tested_rooms = ds_map_create(); //Does get cleared whenever calling rd_connect_rooms_with_type_start
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
		case "hallway":
			return transition.hallway;
		case "door":
			return transition.door;
		case "box":
			return transition.box;
		case "secret":
			return transition.secret;
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

function rd_filter_paths_by_start_and_roomtype(from_room, desired_transition_type,  desired_dir, desired_time, desired_roomtypes, desired_letter = "")
{
	var unfiltered_paths = rd_filter_paths_by_start(from_room, desired_transition_type, desired_dir, desired_time, desired_letter);
	
	if ( ! array_contains(desired_roomtypes, roomtype.oneway) ) //filter out oneway paths from potentialoneway rooms
	{
	
		var filtered_paths = ds_list_create();
	
		for (var i = 0; i < ds_list_size(unfiltered_paths); i++)
		{
			var path = ds_list_find_value(unfiltered_paths, i);
			
			//The path is oneway, unless it is also ratblocked
			if ( (path.startdoor.startonly && !path.startdoor.ratblocked)
			||   (path.exitdoor.exitonly   && !path.exitdoor.ratblocked) )
			{
				//do nothing
			}
			else
			{
				ds_list_add(filtered_paths, path);
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
		path = concat(path, " -> ", next.first.title, " ", next.path.startletter, " to ", next.path.exitletter);
		
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

function rd_get_exit_struct(path)
{
	var exitpair = 
	{
		exittype : path.exittype,
		exitdir : path.exitdir
	};
			
	return exitpair;
}

//TODO: make work with gustavo
function rd_clear_transformation()
{
	global.noisejetpack = false;
	
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
}

//TODO: implement
function rd_give_transformation(name)
{
	with (obj_player)
	{
		switch (name)
		{
			case "barrel":
				rd_barrel();
			case "satan":
				rd_satan();
			default:
				break;
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
