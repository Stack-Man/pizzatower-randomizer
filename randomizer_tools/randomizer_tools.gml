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

function rd_add_connection_rooms_to_map(connection, map)
{
	var debug_msg = "";
	
	var next = connection;
	
	while (next != undefined)
	{
		ds_map_add(map, next.first.title, next.first);
		next = next.second;
		
		//concat(debug_msg, " ", connection.firs
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
