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
	return ds_map_find_value(thisroom, roomvalues.type) == type;
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
	if (ds_map_exists(global.all_rooms,  ds_map_find_value(thisroom, roomvalues.title) ) )
		ds_map_delete(global.all_rooms,  ds_map_find_value(thisroom, roomvalues.title) );
}

function rd_filter_paths_by_start(from_room, desired_type, desired_dir, desired_time, desired_letter = "")
{
	return rd_filter_paths(from_room, desired_type, desired_dir, desired_time, desired_letter, pathvalues.starttype, pathvalues.startdir, pathvalues.startletter);
}

function rd_filter_paths_by_exit(from_room, desired_type, desired_dir, desired_time, desired_letter = "")
{
	return rd_filter_paths(from_room, desired_type, desired_dir, desired_time, desired_letter, pathvalues.exittype, pathvalues.exitdir, pathvalues.exitletter);
}

//TODO: make seeded
function rd_random_seeded(l, r)
{
	//Subtract 1 so that it stays within the bounds of the array
	//Floor it since the value can be a float
	return floor(random(r - 1 - l) + l)
}
