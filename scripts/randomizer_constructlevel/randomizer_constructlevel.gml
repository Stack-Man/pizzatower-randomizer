//TODO: special case for branching john rooms, the construction currently 
//assumes there's at least three transitions but in this case there will be two and you only enter/exit the room once
function rd_construct_levels()
{	
	var level_count = array_length(level_names);
	
	var levels = ds_list_create();
	var entrances = rd_get_rooms_of_type([roomtype.entrance, roomtype.entrancebranching]);
	
	for (var i = 0; i < level_count; i++)
	{
		var first_room = ds_list_find_value(entrances, i);
		var first_room_is_end_branch = rd_check_type(first_room, roomtype.entrance);
		
		show_debug_message( concat("Constructing: ", first_room.title) );
		
		var incomplete_sequence = 
		{
			to_connection : undefined,
			return_connection : undefined,
			next : undefined,
			last_room : first_room,
			last_room_is_end_branch : first_room_is_end_branch
		};
		
		var level = rd_connect_to_branch(incomplete_sequence, "A");
		
		if (level != undefined)
			ds_list_add(levels, level);
		else
			show_debug_message( concat("Failed to construct: ", first_room.title) );
	}
	
	for (var k = 0; k < ds_list_size(levels); k++)
	{
		var level = ds_list_find_value(levels, k);
		rd_add_rooms_to_level(level, 10); //automatically adds the new rooms to global.sequence_tested_rooms
	}
	
	for (var j = 0; j < ds_list_size(levels); j++)
	{
		var level = ds_list_find_value(levels, j);
		rd_link_sequences(level);
	}
	
	//free the memory afterwards
	ds_map_destroy(global.all_rooms);
}

function rd_add_rooms_to_level(sequence,  desired_amount)
{
	var next = sequence;
	var total_added = 0;
	var amount_added_this_loop = -1;
	
	while (next != undefined && amount_added_this_loop != 0 && total_added < desired_amount)
	{
		amount_added_this_loop = 0;
		
		var roomtypes_arr = twoway_types;
		var path_time_arr_to = [pathtime.any];
		
		if (next.return_connection != undefined)
		{
			roomtypes_arr = oneway_types;
			path_time_arr_to = [pathtime.any, pathtime.notpizzatime];
			var path_time_arr_return = [pathtime.any, pathtime.pizzatime];
			
			amount_added_this_loop += rd_add_rooms_inbetween(next.return_connection, roomtypes_arr, path_time_arr_return, desired_amount - total_added - amount_added_this_loop);
		}
			
		
		if (next.to_connection != undefined)
			amount_added_this_loop += rd_add_rooms_inbetween(next.to_connection, roomtypes_arr, path_time_arr_to, desired_amount - total_added);
			

		total_added += amount_added_this_loop;
		next = next.next;
	}
	
	show_debug_message( concat("Rooms Added to ", sequence.to_connection.first.title, ": ", total_added) );
}

function rd_add_rooms_inbetween(connection, roomtypes_arr, path_time_arr, desired_amount)
{
	var next = connection;
	var last = undefined;
	var total_added = 0;

	while (next != undefined)
	{
		var first_room = next.first;
		var actual_second = next.second; //Allows us to add new connections inbetween without looping forever, we'll only add to the original connections
		
		if (next.second != undefined)
		{
			var last_room = next.second.first;
			
			var first_room_start_letter = next.path.startletter;
			var last_room_exit_letter = next.second.path.exitletter;
			
			//Must start with same first start and last exit so that existing connections remain connected
			var new_connection = rd_connect_rooms_with_type_start(first_room, last_room, roomtypes_arr, path_time_arr, first_room_start_letter, "", "", last_room_exit_letter);
			
			if (new_connection != undefined)
			{
				show_debug_message( concat("Added rooms inbetween ", first_room.title, " ", first_room_start_letter, " and ", last_room.title, " ", last_room_exit_letter) );
				show_debug_message("Original Connection: ");
				rd_print_connection_path(next);
				
				show_debug_message("New Connection: ");
				rd_print_connection_path(new_connection);
				
				total_added += rd_count_connections(new_connection);
				
				var temp = next.second;
				rd_add_connection_to_end_replace(new_connection, temp);
				
				//Add the roonms used to sequence_tested_rooms so they aren't reused
				rd_add_connection_rooms_to_map(new_connection, global.sequence_tested_rooms);
				
				//replace next's valuse with new_connection's values
				//because we found a new path for first and next's original second is appendded to the end of new connection
				next.first = new_connection.first;
				next.second = new_connection.second;
				next.path = new_connection.path;
				
				show_debug_message("Final Connection: ");
				rd_print_connection_path(next);
			}
		}
		
		next = actual_second;
	}


	return total_added; //return number of rooms added
}

#region branch sequencing

//sequence struct
//sequence.to_connection = a complete connection struct from a room to last room
//sequence.return_connection = a connection struct IF the last room was an end branch
//sequence.next = the next sequence
//sequence.last_room = the room at the end of sequence.first, where we will start from next
//sequence.last_room_is_end_branch = bool, true if last room was an endbranch

//prev_sequence_last_start_letter: the start letter of the path chosen for the "last room" in a connection for that sqeuence
//the actual path used for that room does not matter, we can repick it, but the letter (the transition) needs to be the same
//or else the new path start won't match the expected transition
function rd_connect_to_branch(sequence, prev_sequence_last_start_letter = "")
{
	show_debug_message( concat("Trying sequnce for ", sequence.last_room.title, " which started at ", prev_sequence_last_start_letter) );
	
	if (sequence.to_connection == undefined) //needs a connection still
	{
		if (sequence.last_room_is_end_branch) //two way to next branch
		{
			var unfiltered_branches = rd_get_rooms_of_type([roomtype.branching, roomtype.john]);
			var branches = rd_filter_out_rooms(unfiltered_branches, global.sequence_tested_rooms);
			
			ds_list_destroy(unfiltered_branches);
			
			for (var i = 0; i < ds_list_size(branches); i++)
			{
				var branch = ds_list_find_value(branches, i);
				
				var connection = rd_connect_rooms_with_type_start(sequence.last_room, branch, twoway_types, pathtime.any, prev_sequence_last_start_letter);
				
				if (connection != undefined)
				{
					var original_last_path = rd_get_last_path(connection); //All that matters is the start since that matches the connection
					
					var possible_last_paths = rd_filter_paths_by_start_and_roomtype(
						branch, 
						original_last_path.starttype, 
						original_last_path.startdir, 
						original_last_path.pathtime,
						twoway_types,
						original_last_path.startletter
						);
					
					rd_add_connection_rooms_to_map(connection, global.sequence_tested_rooms);
					sequence.to_connection = connection;

					//for each possible last path, try to find a sequence
					for (var p = 0; p < ds_list_size(possible_last_paths); p++)
					{
						//There's no need to set the new last path for the last connection room.
						//The previous room and the following room will link the room without using the last connection room's path
						var possible_path = ds_list_find_value(possible_last_paths, p);
						//var last_exit_letter = possible_path.exitletter;
						var last_start_letter = possible_path.startletter;
						
						var last_is_john = rd_check_type(branch, roomtype.john);
					
						if (! last_is_john)
						{
							var incomplete_sequence =
							{
								to_connection : undefined,
								return_connection: undefined,
								next: undefined,
								last_room: branch,
								last_room_is_end_branch: false
							};
						
							var next_sequence = rd_connect_to_branch(incomplete_sequence, last_start_letter);
						
							if (next_sequence != undefined)
							{

								sequence.next = next_sequence;
								return sequence;
							}
							
						}
						else
						{
							return sequence; //return sequence without next
						}
					}
					
					//failed to find sequence with this connection to branch
					rd_remove_connection_rooms_from_map(connection, global.sequence_tested_rooms)
				}
				
				//next connection or sequence failed try next branch
			}
			
			//connection or sequence failed with all branches
			return undefined;
			
		}
		else //one way to next branch and one way return
		{
			var unfiltered_branches = rd_get_rooms_of_type([roomtype.branching, roomtype.johnbranching]);
			var branches = rd_filter_out_rooms(unfiltered_branches, global.sequence_tested_rooms);
			
			ds_list_destroy(unfiltered_branches);
			
			//Try connecting to any branch or john branch
			for (var i = 0; i < ds_list_size(branches); i++)
			{
				var branch = ds_list_find_value(branches, i);
				
				show_debug_message("Doing to_connection");
				var possible_connections = rd_connect_rooms_with_type_start(
					sequence.last_room, 
					branch, 
					oneway_types, 
					[pathtime.any, pathtime.notpizzatime],
					prev_sequence_last_start_letter, "",
					"", "",
					true);
				
				//Try every exit that can create a valid to_connection in case one of them prevents a valid return_connection from being created
				for (var j = 0; j < ds_list_size(possible_connections); j++)
				{
					var connection = ds_list_find_value(possible_connections, j);
					
					if (connection != undefined)
					{
					
						var original_last_path = rd_get_last_path(connection); 
						var possible_last_paths = rd_filter_paths_by_start_and_roomtype(
							branch, 
							original_last_path.starttype, 
							original_last_path.startdir, 
							original_last_path.pathtime, 
							oneway_types,
							original_last_path.startletter //We only care about the start because it needs to match the previous transition
							);
						
						rd_add_connection_rooms_to_map(connection, global.sequence_tested_rooms);
						sequence.to_connection = connection;

						//for each possible last path, try to find a sequence
						for (var p = 0; p < ds_list_size(possible_last_paths); p++)
						{
							var possible_path = ds_list_find_value(possible_last_paths, p);
							var last_exit_letter = possible_path.exitletter;
							var actual_start_letter = connection.path.startletter;
						
							show_debug_message( concat("to_connection with: ", sequence.last_room.title, " ", connection.path.startletter, " to ", connection.path.exitletter, " with ",
							branch.title, " ", possible_path.startletter, " to ", possible_path.exitletter) );
					
							//start transition for the return trip matches the exit transition for the to trip (last_exit_letter)
							//end transition matches the start transition for the to trip (prev_sequence_last_start_letter)

							//The return needs to start from the same exit as the possible path
							//AND end with the same start as the original to room's path
							show_debug_message("Doing return_connection");
							
							var last_is_john = rd_check_type(branch, roomtype.johnbranching);
							
							if (last_is_john) //necessary since the player stays in the john room before using the return connection
								last_exit_letter = possible_path.startletter;
							
							var connection_return = rd_connect_rooms_with_type_start(
								branch, 
								sequence.last_room, 
								oneway_types, 
								[pathtime.any, pathtime.pizzatime], 
								last_exit_letter, "",	//Only care about the first start and the last end, so the first end and the last start are left empty
								"", actual_start_letter);
					
							if (connection_return != undefined)
							{
								var test_last_path = rd_get_last_path(connection_return);
							
								rd_print_connection_path(connection);
								rd_print_connection_path(connection_return);
							
								rd_add_connection_rooms_to_map(connection_return, global.sequence_tested_rooms);
								sequence.return_connection = connection_return; 
					
								if (! last_is_john)
								{
									var incomplete_sequence =
									{
										to_connection : undefined,
										return_connection: undefined,
										next: undefined,
										last_room: branch,
										last_room_is_end_branch: true
									};
						
									//The next sequence starts from the same exit as is used for the end of the to connection and start of the return connection
									var next_sequence = rd_connect_to_branch(incomplete_sequence, last_exit_letter);
						
									if (next_sequence != undefined)
									{
										sequence.next = next_sequence;
										return sequence;
									}
								
								}
								else
								{
									return sequence; //return sequence without next
								}
						
								//failed to find sequence with this connection_return from branch
								rd_remove_connection_rooms_from_map(connection_return, global.sequence_tested_rooms);
							}
						}
					
						//failed to find sequence with this connection to branch
						rd_remove_connection_rooms_from_map(connection, global.sequence_tested_rooms);
					}
					
					//This connection failed, try next connection
				}
			
				//all connections, return connections, or sequence failed, try next branch
			}
			
			//connection, return connection, or sequence failed with all branches
			return undefined;
		}
		
		//Should be unreachable
		return undefined;
	}
	
	//else, sequence is complete, return it
	show_debug_message( concat("sequence complete") );
	return sequence;
}

#endregion

#region connecting

function rd_connect_rooms_with_type_start(first_room, last_room, roomtypes_arr, path_time_arr, start_letter = "", exit_letter = "", last_start_letter = "", last_exit_letter = "", return_list = false)
{
	show_debug_message( concat("Trying connection from ", first_room.title, " ", start_letter, " to ", exit_letter, " with ", last_room.title, " ", last_start_letter, " to ", last_exit_letter));
	
	//Trying new connection, clear tested from last connection
	ds_map_clear(global.connection_tested_rooms);
	ds_list_clear(global.connection_tested_exits);		
	
	var first_paths = rd_filter_paths_by_start_and_roomtype(first_room, transition.none, transitiondir.none, path_time_arr, roomtypes_arr, start_letter);
	var used_exits = ds_list_create();
	
	var connections = ds_list_create();
	
	for (var i = 0; i < ds_list_size(first_paths); i++)
	{
		var first_path = ds_list_find_value(first_paths, i);
		
		if ( first_path.exitletter == exit_letter || exit_letter == "")
		{
			var exitpair = rd_get_exit_struct(first_path);
			
			if (! rd_list_contains_exit(used_exits, exitpair) )
			{
				ds_list_add(used_exits, exitpair);
			
				var incomplete_connection =
				{
					first: first_room,
					path: first_path,
					second: undefined
				};
		
				var connection = rd_connect_rooms_with_type(incomplete_connection, last_room, roomtypes_arr, path_time_arr, last_start_letter, last_exit_letter);
		
				if (connection != undefined) //valid route found
				{
					if (return_list)
					{
						ds_list_add(connections, connection);
					}
					else
					{
						ds_list_destroy(used_exits);
						return connection;
					}
					
				}
			}
		
		}
		
		//else try the next path
	}

	ds_list_destroy(used_exits);
	
	
	if (return_list)
		return connections;
	
	return undefined;
	
}

//returns a connection struct
//connection.first, from room
//connection.path, path in first whose exit matches second.path's start
//connection.second, a connection tuplet (room a, room b, path)
function rd_connect_rooms_with_type(connection, last_room, roomtypes_arr, path_time_arr, last_start_letter = "", last_exit_letter = "")
{
	if (connection.second == undefined) //needs a connection still
	{
		var first_room = connection.first;
		var first_path = connection.path;
		
		var potential_rooms = rd_get_rooms_of_type(roomtypes_arr);

		//Look for room with a start dir that matches
		var potential_matches = rd_get_rooms_with_start_path(
			potential_rooms, 
			first_path.exittype,
			rd_get_opposite_dir(first_path.exitdir),
			path_time_arr );
			
		var valid_matches = ds_list_create();
		
		//remove all rooms in global.current_rooms from valid_matches
		for (var v = 0; v < ds_list_size(potential_matches); v++)
		{
			var potential_match = ds_list_find_value(potential_matches, v);
			
			//If the room title exists in the current rooms map, don't use it
			if (! ds_map_exists(global.sequence_tested_rooms, potential_match.title)
			&& ! ds_map_exists(global.connection_tested_rooms, potential_match.title) )
			{
				ds_list_add( valid_matches, potential_match );
			}
		}
		
		//for each match, look if you can connect it to last, or if you need to find a new room between
		for (var j = 0; j < ds_list_size(valid_matches); j++)
		{
			var match_room =  ds_list_find_value(valid_matches, j);
			
			//remember rooms that have already been attempted in the connection before
			ds_map_add(global.connection_tested_rooms, match_room.title, match_room); 
				
			//Check if there's a path between match and last
				
			//Get the paths with start that matches first's exit
			var first_exit_type = first_path.exittype;
			var first_exit_dir = rd_get_opposite_dir(first_path.exitdir);
			
			//filter out one way paths if one ways aren't allowed
			var match_paths = rd_filter_paths_by_start_and_roomtype(match_room, first_exit_type, first_exit_dir, path_time_arr, roomtypes_arr);

			//For each match path with a good start, check if there's a last path that matches
			for (var k = 0; k < ds_list_size(match_paths); k++)
			{
				var match_path =  ds_list_find_value(match_paths, k);
				
				//get paths from last_room with start that matches match's exit
				var last_paths = rd_filter_paths_by_start_and_roomtype(
					last_room, 
					match_path.exittype, 
					rd_get_opposite_dir(match_path.exitdir), 
					path_time_arr,
					roomtypes_arr,
					last_start_letter);
					
				//If there is at least one valid path
				if ( ds_list_size(last_paths) > 0)
				{
					var last_path =  ds_list_find_value(last_paths, 0)
					var found = false;
					
					if (last_exit_letter != "")
					{
						for (var r = 0; r < ds_list_size(last_paths); r++)
						{
							var potential_last_path = ds_list_find_value(last_paths, r);
							
							if (potential_last_path.exitletter == last_exit_letter)
							{
								found = true;
								last_path = potential_last_path;
								break;
							}
						}
						
						//no valid exit found
					}
					else
					{
						found = true;
					}
					
					//only return if last path matches the exit letter or the last path exit was not cared about
					if (found)
					{
						var connection_last = 
						{
							first: last_room,
							path: last_path, //Not used for linking BUT the start is used as reference when creating the next sequence
							second: undefined //Indicates that it is the end of the connection
						};
					
						var connection_to_last = 
						{
							first: match_room,
							path: match_path,
							second: connection_last
						};
						
						var connection_to_first =
						{
							first: first_room,
							path: first_path,
							second: connection_to_last
						};
					
						//Found a route from first to last
						return connection_to_first;
					}
				}

			}
			
			//exhausted all match paths
			
			var used_exit_types = ds_list_create();
			
			//Try each match path with a new room on the end
			for (var k = 0; k < ds_list_size(match_paths); k++)
			{
				var match_path =  ds_list_find_value(match_paths, k);
				
				var exitpair = rd_get_exit_struct(match_path);
				
				//Don't repeat exit types that have already been tested in the sequence
				//Don't repeat exit types that have already been tested in the room
				if (!rd_list_contains_exit(global.connection_tested_exits, exitpair) && !rd_list_contains_exit(used_exit_types, exitpair)) 
				{
					//try to find a new room inbetween for this match_path which we know has a valid start
					var incomplete_connection = 
					{
						first: match_room,
						path: match_path,
						second: undefined
					};
			
					ds_list_add(global.connection_tested_exits, exitpair);
					ds_list_add(used_exit_types, exitpair);
					
					var next_connection = rd_connect_rooms_with_type(incomplete_connection, last_room, roomtypes_arr, path_time_arr, last_start_letter, last_exit_letter);
			
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

function rd_link_sequences(sequence)
{
	var next = sequence;
	
	while (next != undefined)
	{
		var to = next.to_connection;
		var ret = next.return_connection;
		
		if (to != undefined)
			rd_link_connections(to);
		
		if (ret != undefined)
			rd_link_connections(ret);

		next = next.next;
	}
	
}

function rd_link_connections(connection)
{
	show_debug_message( concat("Connecting: ") );
	rd_print_connection_path(connection);
	
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
	var from_ID = asset_get_index(from_room.title);
	var to_ID = asset_get_index(to_room.title);
	
	var from_letter = from_path.exitletter;
	var to_letter = to_path.startletter;
		
	show_debug_message(concat("connected ", from_room.title, " ", from_letter, " to ", to_room.title, " ", to_letter));
	
	rd_add_path(from_ID, from_letter, to_ID, to_letter);
	
	rd_remove_room(from_room);
	rd_remove_room(to_room);
}

function rd_add_path(current_id, current_letter, destination_id, destination_letter )
{
	var destination =
	{
		roomid : destination_id,
		letter : destination_letter
	};
	
	var reverse =
	{
		roomid : current_id,
		letter : current_letter
	};
	
	//Add current to destination
	if (!ds_map_exists(global.transition_map, current_id))
		ds_map_add(global.transition_map, current_id, ds_map_create())
	
	ds_map_add( ds_map_find_value(global.transition_map, current_id), current_letter, destination);
	
	//Add destination to current (backwards)
	if (!ds_map_exists(global.transition_map, destination_id))
		ds_map_add(global.transition_map, destination_id, ds_map_create())
	
	ds_map_add( ds_map_find_value(global.transition_map, destination_id), destination_letter, reverse);
}

#endregion

//desired_time can be a single value or an array of values
//TODO: add global variable whether doors that were originally a LOOP are allowed
function rd_filter_paths(from_room, desired_type, desired_dir, desired_time, desired_letter, start)
{
	var paths = from_room.paths;
	var valid_paths = ds_list_create();
	
	//find valid path
	for (var i = 0; i < ds_list_size(paths); i++)
	{
		var path =  ds_list_find_value(paths, i);
		
		var p_time = path.pathtime;
		var p_type;
		var p_dir;
		var p_letter;
		
		if (start)
		{
			p_type = path.starttype;
			p_dir = path.startdir;
			p_letter = path.startletter;
		}
		else
		{
			p_type = path.exittype;
			p_dir = path.exitdir;
			p_letter = path.exitletter;
		}
		
		var time_matches = false;
		
		if ( is_array(desired_time) )
		{
			for (var j = 0; j < array_length(desired_time); j++)
			{
				if (p_time == desired_time[j])
				{
					time_matches = true;
					break;
				}
			}
		}
		else
		{
			time_matches = (p_time == desired_time || desired_time == pathtime.none);
		}
		
		
		if (	time_matches
			&& (p_type == desired_type || desired_type == transition.none)
			&& (p_letter == desired_letter || desired_letter == "")
			&& (p_dir == desired_dir || desired_dir == transitiondir.none)
			)
			{
				ds_list_add(valid_paths, path);
			}
		
	}
	
	return valid_paths;
}

//TODO: shuffle seeded the array OR maybe shuffle the all_rooms?
//TODO: shuffle seeded the paths too
function rd_get_rooms_of_type(roomtypes_arr)
{
	var arr = [];
	ds_map_values_to_array(global.all_rooms, arr);
	
	var potential_rooms = ds_list_create();

	for (var i = 0; i < array_length(arr); i++)
	{
		var thisroom = arr[i];
		
		if (array_contains(roomtypes_arr, thisroom.roomtype ) )
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
