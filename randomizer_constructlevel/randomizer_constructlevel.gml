function rd_construct_levels()
{
	var level_count = array_length(level_names);
			
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
			rd_link_sequences(level);
		else
			show_debug_message( concat("Failed to construct: ", first_room.title) );
	}
	
	//free the memory afterwards
	ds_map_destroy(global.all_rooms);
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
				//show_debug_message( concat("Try to connect to branch: ", branch.title) );
				
				var connection = rd_connect_rooms_with_type_start(sequence.last_room, branch, twoway_types, pathtime.any, prev_sequence_last_start_letter);
				
				if (connection != undefined)
				{
					var original_last_path = rd_get_last_path(connection); //All that matters is the start since that matches the connection
					
					var possible_last_paths = rd_filter_paths_by_start(
						branch, 
						original_last_path.starttype, 
						original_last_path.startdir, 
						original_last_path.pathtime, 
						original_last_path.startletter
						);
					
					rd_add_connection_rooms_to_map(connection, global.sequence_tested_rooms);
					sequence.to_connection = connection;
					
					//show_debug_message( concat("Trying paths of size ", ds_list_size(possible_last_paths), " for ", branch.title) );
					
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
						
							//var next_sequence = rd_connect_to_branch(incomplete_sequence, last_exit_letter);
							var next_sequence = rd_connect_to_branch(incomplete_sequence, last_start_letter);
						
							if (next_sequence != undefined)
							{
								//show_debug_message( concat("Successful connect to branch: ", branch.title) );
								
								sequence.next = next_sequence;
								return sequence;
							}
							
							show_debug_message("Failed to connect to not john");
							
						}
						else
						{
							//show_debug_message( concat("Successful to connect to end branch: ", branch.title) );
							show_debug_message("connect to john");
							return sequence; //return sequence without next
						}
					}
					
					//failed to find sequence with this connection to branch
					rd_remove_connection_rooms_from_map(connection, global.sequence_tested_rooms)
				}
				
				//show_debug_message( concat("Failed to connect to branch: ", branch.title) );
				
				//next connection or sequence failed try next branch
			}
			
			//connection or sequence failed with all branches
			//show_debug_message( concat("Failed to connect to any branch") );
			return undefined;
			
		}
		else //one way to next branch and one way return
		{
			var unfiltered_branches = rd_get_rooms_of_type([roomtype.branching, roomtype.johnbranching]);
			var branches = rd_filter_out_rooms(unfiltered_branches, global.sequence_tested_rooms);
			
			ds_list_destroy(unfiltered_branches);
			
			for (var i = 0; i < ds_list_size(branches); i++)
			{
				var branch = ds_list_find_value(branches, i);
				//show_debug_message( concat("Try to connect to branch and return: ", branch.title) );
				
				//start transition matches the end transition for the to trip (prev_sequence_last_start_letter)
				var connection = rd_connect_rooms_with_type_start(sequence.last_room, branch, oneway_types, [pathtime.any, pathtime.notpizzatime], prev_sequence_last_start_letter);
				
				show_debug_message( concat("try connection from ", sequence.last_room.title, " to ", branch.title) );
				
				if (connection != undefined)
				{
					show_debug_message( concat("Used connection from ", sequence.last_room.title, " to ", branch.title) );
					
					//show_debug_message( concat("Connection starts with ", sequence.last_room.title, " ", prev_sequence_last_start_letter) );
					
					var original_last_path = rd_get_last_path(connection); //All that matters is the start since that matches the connection
					var possible_last_paths = rd_filter_paths_by_start(
						branch, 
						original_last_path.starttype, 
						original_last_path.startdir, 
						original_last_path.pathtime, 
						original_last_path.startletter
						);
						
					rd_add_connection_rooms_to_map(connection, global.sequence_tested_rooms);
					sequence.to_connection = connection;
					
					//for each possible last path, try to find a sequence
					for (var p = 0; p < ds_list_size(possible_last_paths); p++)
					{
						var possible_path = ds_list_find_value(possible_last_paths, p);
						//var last_exit_letter = possible_path.exitletter;
						var last_start_letter = possible_path.startletter;
					
						//start transition for the return trip matches the exit transition for the to trip (last_exit_letter)
						//end transition matches the start transition for the to trip (prev_sequence_last_start_letter)
						
						//show_debug_message( concat("Connection might end at ", branch.title, " ", last_exit_letter) );
						
						//var connection_return = rd_connect_rooms_with_type_start(branch, sequence.last_room, oneway_types, [pathtime.any, pathtime.pizzatime], last_exit_letter, prev_sequence_last_start_letter);
						var connection_return = rd_connect_rooms_with_type_start(branch, sequence.last_room, oneway_types, [pathtime.any, pathtime.pizzatime], last_start_letter, prev_sequence_last_start_letter);
					
						show_debug_message( concat("try return from ", branch.title, " to ", sequence.last_room.title) );
					
						if (connection_return != undefined)
						{
							show_debug_message( concat("Used return from ", branch.title, " to ", sequence.last_room.title) );
							
							rd_print_connection_path(connection);
							rd_print_connection_path(connection_return);
							
							//show_debug_message( concat("Connection: ", connection_return ))
							//show_debug_message( concat("Connection Return: ", connection_return ))
							
							var last_is_john = rd_check_type(branch, roomtype.johnbranching);
						
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
						
								//var next_sequence = rd_connect_to_branch(incomplete_sequence, last_exit_letter);
								var next_sequence = rd_connect_to_branch(incomplete_sequence, last_start_letter);
						
								if (next_sequence != undefined)
								{
									//show_debug_message( concat("Successful connect and return to branch: ", branch.title) );
									
									sequence.next = next_sequence;
									return sequence;
								}
								
								show_debug_message("Failed to connect and return to not john");
						
							}
							else
							{
								//show_debug_message( concat("Successful connect and return to end branch: ", branch.title) );
								
								show_debug_message("connect to john");
								
								return sequence; //return sequence without next
							}
						
							//failed to find sequence with this connection_return from branch
							//show_debug_message( concat("Failed to connect return from branch: ", branch.title) );
							rd_remove_connection_rooms_from_map(connection_return, global.sequence_tested_rooms);
						}
					}
					
					//failed to find sequence with this connection to branch
					rd_remove_connection_rooms_from_map(connection, global.sequence_tested_rooms);
				}
			
				//show_debug_message( concat("Failed to connect to branch: ", branch.title) );
				//connection, return connection, or sequence failed, try next branch
			}
			
			//connection, return connection, or sequence failed with all branches
			//show_debug_message( concat("Failed to connect to any branch") );
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

function rd_connect_rooms_with_type_start(first_room, last_room, roomtypes_arr, path_time_arr, start_letter = "", exit_letter = "")
{
	//show_debug_message( concat("Trying connection from ", first_room.title, " to ", last_room.title));
	
	//Trying new connection, clear tested from last connection
	ds_map_clear(global.connection_tested_rooms);
	ds_list_clear(global.connection_tested_exits);		
	
	var first_paths = rd_filter_paths_by_start(first_room, transition.none, transitiondir.none, path_time_arr, start_letter);
	var used_exits = ds_list_create();
	
	//show_debug_message( concat("Trying connection from ", first_room.title, " to ", last_room.title, " with paths of size ", ds_list_size(first_paths) ));
	
	for (var i = 0; i < ds_list_size(first_paths); i++)
	{
		var first_path = ds_list_find_value(first_paths, i);
		
		if ( first_path.exitletter == exit_letter || exit_letter == "")
		{
			var exitpair = 
			{
				exittype : first_path.exittype,
				exitdir : first_path.exitdir
			};
			
			if (! rd_list_contains_exit(used_exits, exitpair) )
			{
				ds_list_add(used_exits, exitpair);
			
				var incomplete_connection =
				{
					first: first_room,
					path: first_path,
					second: undefined
				};
		
				var connection = rd_connect_rooms_with_type(incomplete_connection, last_room, roomtypes_arr, path_time_arr);
		
				if (connection != undefined) //valid route found
				{
					ds_list_destroy(used_exits);
					
					//show_debug_message( concat("Successful connection from ", first_room.title, " to ", last_room.title));
					return connection;
				}
			}
		
		}
		
		//else try the next path
	}

	ds_list_destroy(used_exits);
	
	//show_debug_message( concat("Failed connection from ", first_room.title, " to ", last_room.title));
	return undefined;
	
}

//returns a connection struct
//connection.first, from room
//connection.path, path in first whose exit matches second.path's start
//connection.second, a connection tuplet (room a, room b, path)
function rd_connect_rooms_with_type(connection, last_room, roomtypes_arr, path_time_arr)
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
			var match_paths = rd_filter_paths_by_start(match_room, first_exit_type, first_exit_dir, path_time_arr);

			//For each match path with a good start, check if there's a last path that matches
			for (var k = 0; k < ds_list_size(match_paths); k++)
			{
				var match_path =  ds_list_find_value(match_paths, k);
				
				//get paths from last_room with start that matches match's exit
				var last_paths = rd_filter_paths_by_start(
					last_room, 
					match_path.exittype, 
					rd_get_opposite_dir(match_path.exitdir), 
					path_time_arr);
					
				//If there is at least one valid path
				if ( ds_list_size(last_paths) > 0)
				{
					var connection_last = 
					{
						first: last_room,
						path:  ds_list_find_value(last_paths, 0), //Not used for linking BUT the start is used as reference when creating the next sequence
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

				//This exit didnt work for last, later we will filter rooms that dont have a unique exit type that wasn't tested yet
				var exitpair = 
				{
					exittype : match_path.exittype,
					exitdir : match_path.exitdir
				};
			}
			
			//exhausted all match paths
			
			var used_exit_types = ds_list_create();
			
			//Try each match path with a new room on the end
			for (var k = 0; k < ds_list_size(match_paths); k++)
			{
				var match_path =  ds_list_find_value(match_paths, k);
				
				var exitpair = 
				{
					exittype : match_path.exittype,
					exitdir : match_path.exitdir
				};
				
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
					
					var next_connection = rd_connect_rooms_with_type(incomplete_connection, last_room, roomtypes_arr, path_time_arr);
			
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

//PRIORITY TODO: fix entarnce_4 to be left, keeping it right so that it produces the same layout for debugging :)
//PRIORITY TODO: farm_1 F is being used multiple times, might be having trouble keeping track of which path to actually use for the return trip
//it uses it to enter the branch room then uses it again to leave

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
function rd_filter_paths(from_room, desired_type, desired_dir, desired_time, desired_letter, start)
{
	var paths = from_room.paths;
	var valid_paths = ds_list_create();
	
	//show_debug_message( concat("filtering from paths of size ", ds_list_size(paths)) );
	
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
			//show_debug_message( concat("checking times from array of size ", array_length(desired_time), "for path ", i) );
	
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
			//show_debug_message( concat("checking times not array ") );
			
			time_matches = (p_time == desired_time || desired_time == pathtime.none);
		}
		
		
		if (	time_matches
			&& (p_type == desired_type || desired_type == transition.none)
			&& (p_letter == desired_letter || desired_letter == "")
			&& (p_dir == desired_dir || desired_dir == transitiondir.none)
			)
			{
				//show_debug_message( concat("added path") );
				
				ds_list_add(valid_paths, path);
			}
		else
		{
			//show_debug_message( concat("did not add path") );
		}
		
	}
	
	return valid_paths;
}

//TODO: shuffle seeded the array
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
