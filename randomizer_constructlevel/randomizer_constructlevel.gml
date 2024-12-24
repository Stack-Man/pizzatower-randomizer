function rd_construct_levels()
{
	var level_count = array_length(level_names);
	var levels = ds_map_create();
	
	//TODO: shuffle all rooms map opr something
	
	//Pick entrance and john
	for (var i = 0; i < level_count; i++)
	{
		show_debug_message( concat("Constructing ", level_names[i]) );
		
		var level = ds_map_create()	
		ds_map_add(levels, level_names[i], level);
			
		var entrances = rd_get_rooms_of_type([roomtype.entrance, roomtype.entrancebranching]);
			
		for (var i = 0; i < ds_list_size(entrances); i++)
		{
			var entrance = ds_list_find_value(entrances, i);
				
			var johns = rd_get_rooms_of_type([roomtype.john, roomtype.johnbranching]);
			ds_list_shuffle(johns); //TODO: shuffle seeded
				
			for (var j = 0; j < ds_list_size(johns); j++)
			{
				var john = ds_list_find_value(johns, j);
					
				if (entrance != undefined && john != undefined)
				{
					ds_map_clear(global.current_rooms); //clear all used rooms from memory. global.all_rooms should be updated if the room was actually used
					ds_list_clear(global.invalid_exits); //new connnection so renew exits
				
					show_debug_message( concat( "entrance: ", ds_map_find_value(entrance, roomvalues.title), " john: ", ds_map_find_value(john, roomvalues.title) ));
				
					var connection = rd_connect_rooms_with_type_start(
					entrance, 
					john, 
					[roomtype.twoway, roomtype.ratblockedtwoway, roomtype.potentialoneway, roomtype.oneway, roomtype.branching, roomtype.potentialratblockedtwoway],
					pathtime.any,
					"A" //make sure that the entrance door is used as the start path
					);
				
					if (connection != undefined)
					{
						rd_remove_room(john);
						rd_remove_room(entrance);
						rd_link_connections(connection);
							
						show_debug_message( concat("Successfully constructed ", ds_map_find_value(entrance, roomvalues.title), " to ", ds_map_find_value(john, roomvalues.title) ) );
							
						break; //found a valid john, skip the rest of the johns
					}
					else
					{
						show_debug_message( concat("Failed to construct ", ds_map_find_value(entrance, roomvalues.title), " to ", ds_map_find_value(john, roomvalues.title) ) );
					}
							
				}
					
			}
		
		}
		
	}
	
	//Picking branching logic:
	//Take the current end room
	//for every new end room we're trying to connect to some room, purge memory of invalid exits/rooms
	//also have a chance to pick the john room instead of another branch
	//if an end branch
		//for every branch room
			//try connect two way
			
		//if exhausted all branches
			//step back and undo the last connect one way
			
	//if a start branch
		//for every branch room
			//try connenct one way
			//if successfull
				//try connect backwards one way

		//if exhausted all branches
			//step back and undo the last connect two way
	
	//free the memory afterwards
	ds_map_destroy(global.all_rooms);
}

#region connecting

function rd_connect_rooms_with_type_start(first_room, last_room, roomtypes_arr, path_time, start_letter = "")
{
	var first_paths = rd_filter_paths_by_start(first_room, transition.none, transitiondir.none, path_time, start_letter);
	
	for (var i = 0; i < ds_list_size(first_paths); i++)
	{
		var first_path = ds_list_find_value(first_paths, i);
		
		incomplete_connection =
		{
			first: first_room,
			path: first_path,
			second: undefined
		};
		
		var connection = rd_connect_rooms_with_type(incomplete_connection, last_room, roomtypes_arr, path_time);
		
		if (connection != undefined) //valid route found
			return connection;
			
		//else try the next path
	}

	return undefined;
	
}

//returns a connection
//connection.first, from room
//connection.path, path in first whose exit matches second.path's start
//connection.second, a connection tuplet (room a, room b, path)
function rd_connect_rooms_with_type(connection, last_room, roomtypes_arr, path_time)
{
	show_debug_message( concat("rooms: ", global.recursion_rooms) );
	
	if (connection.second == undefined) //needs a connection still
	{
		
		
		var first_room = connection.first;
		var first_path = connection.path;
		
		var potential_rooms = rd_get_rooms_of_type(roomtypes_arr);

		//Look for room with a start dir that matches
		var potential_matches = rd_get_rooms_with_start_path(
			potential_rooms, 
			ds_map_find_value(first_path, pathvalues.exittype),
			rd_get_opposite_dir(ds_map_find_value(first_path, pathvalues.exitdir)),
			path_time );
			
		var valid_matches = ds_list_create();
		
		//remove all rooms in global.current_rooms from valid_matches
		for (var v = 0; v < ds_list_size(potential_matches); v++)
		{
			var potential_match = ds_list_find_value(potential_matches, v);
			
			//If the room title exists in the current rooms map, don't use it
			if (! ds_map_exists(global.current_rooms, ds_map_find_value(potential_match, roomvalues.title)) )
			{
				ds_list_add( valid_matches, potential_match );
			}
		}
		
		//for each match, look if you can connect it to last, or if you need to find a new room between
		for (var j = 0; j < ds_list_size(valid_matches); j++)
		{
			//Add match room to global.current rooms
			var match_room =  ds_list_find_value(valid_matches, j);
			
			//remember rooms that have already been attempted in the sequence before
			ds_map_add(global.current_rooms, ds_map_find_value(match_room, roomvalues.title), match_room); 
				
			//Check if there's a path between match and last
				
			//Get the paths with start that matches first's exit
			var first_exit_type = ds_map_find_value(first_path, pathvalues.exittype);
			var first_exit_dir = rd_get_opposite_dir(ds_map_find_value(first_path, pathvalues.exitdir));
			var match_paths = rd_filter_paths_by_start(match_room, first_exit_type, first_exit_dir, path_time);

			//For each match path with a good start, check if there's a last path that matches
			for (var k = 0; k < ds_list_size(match_paths); k++)
			{
				var match_path =  ds_list_find_value(match_paths, k);
				
				//get paths from last_room with start that matches match's exit
				var last_paths = rd_get_valid_paths(
					ds_map_find_value(last_room, roomvalues.paths), 
					ds_map_find_value(match_path, pathvalues.exittype),
					path_time,
					rd_get_opposite_dir(ds_map_find_value(match_path, pathvalues.exitdir))
					);
					
				//If there is at least one valid path
				if ( ds_list_size(last_paths) > 0)
				{
					var last_path = ds_list_find_value(last_path, rd_random_seeded(0, ds_list_size(last_path) ));
					
					connection_last = 
					{
						first: last_room,
						path: last_path,
						second: undefined //Indicates that it is the end of the sequence
					};
					
					connection_to_last = 
					{
						first: match_room,
						path: match_path,
						second: connection_last
					};
						
					connection_to_first =
					{
						first: first_room,
						path: first_path,
						second: connection_to_last
					};
					
					//Found a route from first to last
					return connection_to_first;
				}

				//This exit didnt work for last, later we will filter rooms that dont have a unique exit type that wasn't tested yet
				exitpair = 
				{
					type : ds_map_find_value(match_path, pathvalues.exittype),
					dir : ds_map_find_value(match_path, pathvalues.exitdir)
				};
			}
			
			//exhausted all match paths
			
			var used_exit_types = ds_list_create();
			
			//Try each match path with a new room on the end
			for (var k = 0; k < ds_list_size(match_paths); k++)
			{
				var match_path =  ds_list_find_value(match_paths, k);
				
				exitpair = 
				{
					exittype : ds_map_find_value(match_path, pathvalues.exittype),
					exitdir : ds_map_find_value(match_path, pathvalues.exitdir)
				};
				
				//Don't repeat exit types that have already been tested in the sequence
				//Don't repeat exit types that have already been tested in the room
				if (!rd_list_contains_exit(global.invalid_exits, exitpair) && !rd_list_contains_exit(used_exit_types, exitpair)) 
				{
					//try to find a new room inbetween for this match_path which we know has a valid start
					incomplete_connection = 
					{
						first: match_room,
						path: match_path,
						second: undefined
					};
			
					//debug string
					var temp = global.recursion_rooms;
					global.recursion_rooms = concat(global.recursion_rooms, " ", ds_map_find_value(match_room, roomvalues.title) );
					
					ds_list_add(global.invalid_exits, exitpair);
					ds_list_add(used_exit_types, exitpair);
					
					var next_connection = rd_connect_rooms_with_type(incomplete_connection, last_room, roomtypes_arr, path_time);
					
					global.recursion_rooms = temp;
			
					//If didn't find a valid connection and alrady used all matches, return undefined
					if (next_connection == undefined && j >= ds_list_size(valid_matches) )
					{
						return undefined;
					}

					//valid found, return it
					if (next_connection != undefined && next_connection.second != undefined) //a valid connection was found
					{
						//return next_connection;
						connection.second = next_connection;
						return connection;
					}
				}
				
			}
			
			ds_list_destroy(used_exit_types);
				
			//else try the next match_room
		}
		

		//exhausted all matches for first_path
		return undefined;
	}
	
	//else, connection is complete, just return it
	return connection;
}

function rd_link_connections(connection)
{
	var next = connection;
	
	while (next != undefined)
	{
		var from = next.first;
		var from_path = next.path;
		
		if (next.second != undefined)
		{
			var to = next.second.first;
			var to_path = next.second.path;
			
			rd_add_path_with_room(from, from_path, to, to_path);
		}
		
		next = next.second;
	}
}

function rd_add_path_with_room(from_room, from_path, to_room, to_path)
{
	var from_ID = asset_get_index(ds_map_find_value(from_room, roomvalues.title));
	var to_ID = asset_get_index(ds_map_find_value(to_room, roomvalues.title));
	
	var from_letter = ds_map_find_value(from_path, pathvalues.exitletter);
	var to_letter = ds_map_find_value(to_path, pathvalues.startletter);
		
	show_debug_message(concat("connected ", ds_map_find_value(from_room, roomvalues.title), " to ", ds_map_find_value(to_room, roomvalues.title) ));
	
	rd_add_path(from_ID, from_letter, to_ID, to_letter);
	
	rd_remove_room(from_room);
	rd_remove_room(to_room);
}

function rd_add_path(current_id, current_letter, destination_id, destination_letter )
{
	var destination = ds_map_create();
	ds_map_add(destination, destinationvalues.roomid, destination_id);
	ds_map_add(destination, destinationvalues.letter, destination_letter);
	
	var reverse = ds_map_create();
	ds_map_add(reverse, destinationvalues.roomid, current_id);
	ds_map_add(reverse, destinationvalues.letter, current_letter);
	
	//Add current to destination
	if (!ds_map_exists(global.transition_map, current_id))
	{
		ds_map_add(global.transition_map, current_id, ds_map_create())
	}
	
	ds_map_add( ds_map_find_value(global.transition_map, current_id), current_letter, destination);
	
	//Add destination to current (backwards)
	if (!ds_map_exists(global.transition_map, destination_id))
	{
		ds_map_add(global.transition_map, destination_id, ds_map_create())
	}
	
	ds_map_add( ds_map_find_value(global.transition_map, destination_id), destination_letter, reverse);
	

}

#endregion

function rd_filter_paths(from_room, desired_type, desired_dir, desired_time, desired_letter, type_type, dir_type, letter_type)
{
	var paths = ds_map_find_value(from_room, roomvalues.paths);
	var valid_paths = ds_list_create();
	
	//find valid path
	for (var i = 0; i < ds_list_size(paths); i++)
	{
		var path =  ds_list_find_value(paths, i);
		
		var p_time = ds_map_find_value(path, pathvalues.pathtime);
		var p_type = ds_map_find_value(path, type_type);
		var p_dir = ds_map_find_value(path, dir_type);
		var p_start = ds_map_find_value(path,letter_type);
		
		if ((desired_time == p_time || p_time == pathtime.none) 
			&& (desired_type == p_type || p_type == transition.none)
			&& (p_start == desired_letter || desired_letter == "")
			&& (desired_dir == p_dir || p_dir == transitiondir.none)
			)
			{
				ds_list_add(valid_paths, path);
			}
			
	}
	
	return valid_paths;
}

function rd_get_rooms_of_type(roomtypes_arr)
{
	var arr = [];
	ds_map_values_to_array(global.all_rooms, arr);
	
	var potential_rooms = ds_list_create();

	for (var i = 0; i < array_length(arr); i++)
	{
		var thisroom = arr[i];
		
		if (array_contains(roomtypes_arr, ds_map_find_value(thisroom, roomvalues.type) ) )
		{
			ds_list_add(potential_rooms, thisroom);
		}
			
	}

	if (ds_list_size(potential_rooms) == 0)
		return undefined;
	
	return potential_rooms;
}

function rd_get_rooms_with_start_path(potential_rooms, start_type, start_dir, path_time)
{
	var result_rooms = ds_list_create();
	
	for (var i = 0; i < ds_list_size(potential_rooms); i++)
	{
		var potential_room =  ds_list_find_value(potential_rooms, i);
		var paths = rd_filter_paths_by_start(potential_room, start_type, start_dir, path_time);
		
		if ( ds_list_size(paths) > 0 )
			ds_list_add(result_rooms, potential_room);
	}
	
	return result_rooms;
}
