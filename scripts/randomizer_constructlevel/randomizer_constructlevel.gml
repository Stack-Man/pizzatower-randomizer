function rd_construct_levels()
{	
	var levels = ds_list_create();
	var unsorted_entrances = rd_get_rooms_of_type([roomtype.entrance, roomtype.entrancebranching]);
	var entrances = rd_prioritize_rooms_of_type(unsorted_entrances, [roomtype.entrance, roomtype.entrancebranching])
	
	ds_list_destroy(unsorted_entrances);
	
	var war_exit_created = false;
	
	for (var i = 0; i < ds_list_size(entrances); i++)
	{
		var first_room = ds_list_find_value(entrances, i);		
		show_debug_message( concat("Constructing: ", first_room.title) );
		
		var branch_start = ds_list_size( rd_filter_out_rooms(rd_get_rooms_of_type([roomtype.branchstart]), global.sequence_tested_rooms) );
		var branch_any = ds_list_size( rd_filter_out_rooms(rd_get_rooms_of_type([roomtype.branchany]), global.sequence_tested_rooms) );
		var branch_end = ds_list_size( rd_filter_out_rooms(rd_get_rooms_of_type([roomtype.branchend]), global.sequence_tested_rooms) );
		var branch_mid = ds_list_size( rd_filter_out_rooms(rd_get_rooms_of_type([roomtype.branchmid]), global.sequence_tested_rooms) );
		var john = ds_list_size( rd_filter_out_rooms(rd_get_rooms_of_type([roomtype.john]), global.sequence_tested_rooms) );
		var john_branch = ds_list_size( rd_filter_out_rooms(rd_get_rooms_of_type([roomtype.johnbranching]), global.sequence_tested_rooms) );
		
		show_debug_message( concat( "Remaining rooms: ",
		"branch anys left: ", branch_any,
		"branch starts left: ", branch_start, "branch ends left: ", branch_end, 
		"branch mid left: ", branch_mid, "john left: ", john,
		"branch johns left: ", john_branch) );

		var incomplete_sequence = rd_get_sequence_struct(
			undefined, 
			undefined, 
			undefined, 
			first_room, 
			rd_check_type(first_room, roomtype.entrance) );
		
		global.recursion_depth = 0;
		var level = rd_connect_to_branch2(incomplete_sequence, "A");
		
		if (level != undefined)
		{
			show_debug_message( concat("Success to construct: ", first_room.title ) );
			ds_list_add(global.created_levels, asset_get_index(first_room.title));
			ds_list_add(levels, level);
		}	
		else
		{
			show_debug_message( concat("Failed to construct: ", first_room.title) );
			
			if (!war_exit_created)
			{
				show_debug_message( concat("Constructing: ", first_room.title, " with war exit") );
					
				var war_exit_level = rd_connect_to_war_exit(first_room, "A");
				
				if (war_exit_level != undefined)
				{
					ds_list_add(global.created_levels, asset_get_index(first_room.title));
					ds_list_add(levels, war_exit_level);
					war_exit_created = true;
					
					show_debug_message( concat("Success to construct: ", first_room.title, " with war exit") );
				}
				else
				{
					show_debug_message( concat("Failed to construct: ", first_room.title, " with war exit") );
				}
			}
			
			
		}
			
	}
	
	show_debug_message( concat("Created ", ds_list_size(levels), " levels") );
	
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
	
	return ds_list_size(levels);
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

//TODO: not adding rooms properly
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
			
			var first_room_start_letter = next.path.startdoor.letter;
			var last_room_exit_letter = next.second.path.exitdoor.letter;
			
			//Must start with same first start and last exit so that existing connections remain connected
			var new_connections = rd_find_connections_start(
			first_room, last_room, roomtypes_arr, path_time_arr, 
			first_room_start_letter, "", 
			"", last_room_exit_letter,
			true, true,
			true, true,
			false, false,
			false);
			
			if (ds_list_size(new_connections) > 0)
			{
				var new_connection = ds_list_find_value(new_connections, 0);
				
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

function rd_connect_to_war_exit(first_room)
{
	var war_exit_room = ds_list_find_value( rd_get_rooms_of_type([roomtype.warexit]), 0);
	
	var connections = rd_find_connections_start(
			first_room,
			war_exit_room,
			oneway_types,
			[pathtime.any, pathtime.notpizzatime],
			"A", "",
			"", "",
			true, true,
			true, true,
			false, false); 
	
	if ( ds_list_size(connections) > 0)
	{
		var new_sequence = rd_get_sequence_struct(
			ds_list_find_value(connections, 0),
			undefined,
			undefined,
			first_room,
			true);
		
		return new_sequence;
	}
	
	return undefined;
}

//sequence struct
//sequence.to_connection = a complete connection struct from a room to last room
//sequence.return_connection = a connection struct IF the last room was an end branch
//sequence.next = the next sequence
//sequence.last_room = the room at the end of sequence.first, where we will start from next
//sequence.last_room_is_end_branch = bool, true if last room was an endbranch

//prev_sequence_last_path_start_letter: the start letter of the path chosen for the "last room" in a connection for that sqeuence
//the actual path used for that room does not matter, we can repick it, but the letter (the transition) needs to be the same
//or else the new path start won't match the expected transition
function rd_connect_to_branch2(sequence, prev_sequence_last_path_start_letter)
{
	if (sequence.to_connection != undefined)
		return sequence;
	
	global.recursion_depth++;
	
	show_debug_message( concat(rd_buffer(), "Sequence from ", sequence.last_room.title, " ", prev_sequence_last_path_start_letter, " needs return? : ", ! sequence.last_room_is_end_branch));
	
	var needs_return = ! sequence.last_room_is_end_branch; //Still need this variable in case last room is branchany

	var roomtypes = needs_return ? oneway_types : twoway_types;
	var to_pathtimes = needs_return ? [pathtime.any, pathtime.notpizzatime] : [pathtime.any, pathtime.notpizzatime]; 
	
	var johntype = needs_return ? roomtype.johnbranching : roomtype.john;
	var branchtype = needs_return ?  roomtype.branchend : roomtype.branchstart;
	
	var all_branchtypes = global.recursion_depth >= max_branches ? [johntype] : [roomtype.branchany, branchtype, johntype];
	
	var unfiltered_branches = rd_get_rooms_of_type(all_branchtypes); //TODO: allow branchmid if needs_return, and if branchmid is used, ask for anoth4r branchend with branchmid
	var unsorted_branches = rd_filter_out_rooms(unfiltered_branches, global.sequence_tested_rooms);
	var branches = rd_prioritize_rooms_of_type(unsorted_branches, [branchtype, roomtype.branchany, johntype]); //prefer start/end over any, to increase chances of successful construction
	
	ds_list_destroy(unsorted_branches);
	ds_list_destroy(unfiltered_branches);
	
	var use_branch_start = !needs_return
	var use_branch_exit = needs_return;
	
	for (var b = 0; b < ds_list_size(branches); b++)
	{
		show_debug_message(concat(rd_buffer(), "branch ", b  + 1, " of ", ds_list_size(branches) ));
		var branch = ds_list_find_value(branches, b);
		
		//Find all connections
		var connections = rd_find_connections_start(
			sequence.last_room,
			branch,
			roomtypes,
			to_pathtimes,
			prev_sequence_last_path_start_letter, "",
			"", "",
			true, true,
			true, true,
			use_branch_start, use_branch_exit); 
			//if it does not need a return, then it is the end branch, meaning it should enter the next branch from a branch door
			//if it does need a return, then it is a start branch, so it should exit the next branch from a branch door
			
		
		for (var c = 0; c < ds_list_size(connections); c++)
		{
			//show_debug_message(concat(rd_buffer(), "connection ", c + 1, " of ", ds_list_size(connections) ));
			
			var connection = ds_list_find_value(connections, c);
			rd_add_connection_rooms_to_map(connection, global.sequence_tested_rooms);
			sequence.to_connection = connection;
			
			//Find possible paths leaving the connection's last room with the same start
			var original_last_path = rd_get_last_path(connection); 
			var last_paths = rd_filter_paths_by_start_and_roomtype(
				branch, 
				original_last_path.startdoor.type, 
				original_last_path.startdoor.dir, 
				original_last_path.pathtime, 
				roomtypes,
				original_last_path.startdoor.letter,  //Start needs to match the previous room's transition
				use_branch_start, use_branch_exit
				);
			
			for (var l = 0; l < ds_list_size(last_paths); l++)
			{
				//show_debug_message(concat(rd_buffer(), "last path ", l  + 1, " of ", ds_list_size(last_paths) ));
				
				var last_path = ds_list_find_value(last_paths, l);
				var last_is_john = rd_check_type(branch, johntype);
				
				if (!needs_return)
				{
					var new_sequence = rd_continue_sequence(
						sequence, 
						last_is_john,
						branch,
						true,
						last_path.startdoor.letter);
					
					if (new_sequence != undefined)
						return new_sequence;
				}
				
				//If john there is no third door, the player immediately uses the return connection
				var last_exit_letter = last_is_john ? last_path.startdoor.letter : last_path.exitdoor.letter; 
				var actual_start_letter = connection.path.startdoor.letter;
				
				show_debug_message( concat(rd_buffer(), "depth: ", global.recursion_depth, " trying return from ", branch.title, " to ", sequence.last_room.title) );
				
				var return_connections = rd_find_connections_start(
					branch,
					sequence.last_room,
					roomtypes,
					[pathtime.any, pathtime.pizzatime],
					last_exit_letter, last_path.startdoor.letter,
					connection.path.exitdoor.letter, actual_start_letter,
					true, false,
					false, true,
					false, false);

				for (var r = 0; r < ds_list_size(return_connections); r++)
				{
					//show_debug_message(concat(rd_buffer(), "return ", r, " of ", ds_list_size(return_connections) ));
					
					var return_connection = ds_list_find_value(return_connections, r);
					rd_add_connection_rooms_to_map(return_connection, global.sequence_tested_rooms);
					sequence.return_connection = return_connection;
						
					//The next sequence needs to know the start letter of the final path, it may choose a path with a different exit but same start
					var new_sequence = rd_continue_sequence(
						sequence,
						last_is_john,
						branch,
						false,
						last_path.startdoor.letter);
						
					if (new_sequence != undefined)
						return new_sequence;	
						
					rd_remove_connection_rooms_from_map(return_connection, global.sequence_tested_rooms);
					sequence.return_connection = undefined;
				}
					
				//Failed to continue sequence, try next path
			}
			
			//Failed to continue sequence, try next connection
			rd_remove_connection_rooms_from_map(connection, global.sequence_tested_rooms);
			sequence.to_connection = undefined;
		}
		
		//Failed to continue sequence, try next branch
	}
	
	//Failed to find any sequence
	return undefined;
}

function rd_continue_sequence(sequence, last_is_john, last_room, last_room_is_end_branch, prev_sequence_last_path_start_letter)
{
	if (! last_is_john)
	{
		var incomplete_sequence = rd_get_sequence_struct(
		undefined,
		undefined,
		undefined,
		last_room,
		!last_room_is_end_branch); //inverse the end branch
						
		//The next sequence starts from the same exit as is used for the end of the to connection and start of the return connection
		var next_sequence = rd_connect_to_branch2(incomplete_sequence, prev_sequence_last_path_start_letter);
					
		global.recursion_depth--;
		
		if (next_sequence != undefined)
		{
			sequence.next = next_sequence;
			return sequence;
		}

		return undefined; //Tell the calling function to continue its loop					
	}
	
	return sequence; //return sequence without next
}

#endregion

#region connecting

function rd_find_connections_start(first_room, last_room, roomtypes, pathtimes, 
start_letter = "", exit_letter = "", last_start_letter = "", last_exit_letter = "", 
use_start = true, use_exit = true, use_last_start = true, use_last_exit = true,
use_branch_start = false, use_branch_exit = false, try_connect_start = true)
{	
	//show_debug_message( concat(rd_buffer(), "Clearing exit types") );
	ds_list_clear(global.connection_tested_exits);
	ds_map_clear(global.connection_tested_rooms);
	
	global.test_string = concat("depth: ", global.recursion_depth, " start ", first_room.title);
	
	var first_paths =  rd_filter_paths_by_start_and_roomtype(
			first_room, 
			transition.none, transitiondir.none, 
			pathtimes, roomtypes
			);
			
	var connections = ds_list_create();
	
	//Try to connect all paths directly to last room
	//All possible connections are returned;
	
	if (try_connect_start) //false if we are adding rooms inbetween
	{
		for (var f = 0; f < ds_list_size(first_paths); f++)
		{
			var first_path = ds_list_find_value(first_paths, f);
		
			var correct_start = start_letter == "" || (use_start && start_letter == first_path.startdoor.letter) || (!use_start && start_letter != first_path.startdoor.letter);
			var correct_exit = exit_letter == "" || (use_exit && exit_letter == first_path.exitdoor.letter) || (!use_exit && exit_letter != first_path.exitdoor.letter);
		
			if (correct_start && correct_exit)
			{
				var temp = global.test_string;
			
				global.test_string = concat(global.test_string, " ", first_path.exitdoor.letter, " -> ", last_room.title);
			
				var direct_connection = rd_connect_directly(
					first_room, first_path, last_room, roomtypes, pathtimes, 
					last_start_letter, last_exit_letter, 
					use_last_start, use_last_exit, 
					use_branch_start, use_branch_exit);
			
				global.test_string = temp;
			
				if (direct_connection != undefined)
					ds_list_add(connections, direct_connection);
				
			}
		}
	}
	
	if ( ds_list_size(connections) > 0) //If we directly connected, there's no need to test any proper connections
		return connections;
	
	//Try to create connections to last room with all first paths 
	for (var f = 0; f < ds_list_size(first_paths); f++)
	{
		var temp = global.test_string;
		
		var first_path = ds_list_find_value(first_paths, f);
		
		global.test_string = concat(global.test_string, " ", first_path.exitdoor.letter);
		
		var correct_start = start_letter == "" || (use_start && start_letter == first_path.startdoor.letter) || (!use_start && start_letter != first_path.startdoor.letter);
		var correct_exit = exit_letter == "" || (use_exit && exit_letter == first_path.exitdoor.letter) || (!use_exit && exit_letter != first_path.exitdoor.letter);
		
		//show_debug_message( concat("proper connection: ", start_letter, ", ", exit_letter, ", use: ", use_start, ", ", use_exit, ", actual: ", first_path.startdoor.letter, ", ", first_path.exitdoor.letter) );
		
		if (correct_start && correct_exit)
		{
			//Don't repeat exits that have been tested in the connection before
			var exitpair = rd_get_exit_struct(first_path);
			
			if (rd_list_contains_exit(global.connection_tested_exits, exitpair) )
				continue;
			
			//show_debug_message( concat(rd_buffer(), "start No longer trying exits of type: ", exitpair) );
			
			ds_list_add(global.connection_tested_exits, exitpair);
				
			var incomplete_connection = rd_get_connection_struct(
				first_room,
				first_path,
				undefined);
					
			//Only one connection from the list will be used, so we can try to reuse rooms
			ds_map_clear(global.connection_tested_rooms);
				
			var new_connection = rd_find_connections(
				incomplete_connection,
				last_room,
				roomtypes,
				pathtimes,
				last_start_letter, last_exit_letter,
				use_last_start, use_last_exit,
				use_branch_start, use_branch_exit);
				
			if (new_connection != undefined)
				ds_list_add(connections, new_connection);
		}
		
		global.test_string = temp;
		//Try next first path
	}
	
	ds_list_destroy(first_paths);
	
	return connections;
}

function rd_find_connections(connection, last_room, roomtypes, pathtimes, 
last_start_letter = "", last_exit_letter = "", 
use_last_start = true, use_last_exit = true,
use_branch_start = false, use_branch_exit = false)
{
	//Already complete
	if (connection.second != undefined)
		return connection;
	
	var first_room = connection.first;
	var first_path = connection.path;
	
	//Find all rooms that match the first_path
	var potential_rooms = rd_get_rooms_of_type(roomtypes);
	var potential_matches = rd_get_rooms_with_start_path( 
		potential_rooms,
		first_path.exitdoor.type,
		rd_get_opposite_dir(first_path.exitdoor.dir),
		pathtimes
		);
		
	var match_rooms = ds_list_create(); //TODO: delete list

	//remove rooms already being tested in the sequence or connection
	for (var pm = 0; pm < ds_list_size(potential_matches); pm++)
	{
		var potential_match = ds_list_find_value(potential_matches, pm);
			
		//If the room title exists in the current rooms map, don't use it
		if (! ds_map_exists(global.sequence_tested_rooms, potential_match.title)
		&& ! ds_map_exists(global.connection_tested_rooms, potential_match.title) )
		{
			ds_list_add(match_rooms, potential_match );
		}
	}
				
	ds_list_destroy(potential_rooms);
	ds_list_destroy(potential_matches);
				
	var stored_match_paths = ds_list_create(); //TODO: delete list, sub lists are handled
		var temp_used_exits = ds_list_create();
	
	//DEBUG: print match rooms
	/*var test_match_rooms = "";
	
	for (var mr = 0; mr < ds_list_size(match_rooms); mr++)
	{
		test_match_rooms = concat(test_match_rooms, ", ", ds_list_find_value(match_rooms, mr).title );
	}
	
	show_debug_message( concat("Match Rooms: ", test_match_rooms) );*/
	
	//Try to find a match room that connects to last
	for (var mr = 0; mr < ds_list_size(match_rooms); mr++)
	{
		var match_room = ds_list_find_value(match_rooms, mr);

		var temp = global.test_string;

		global.test_string = concat(global.test_string, " -> direct ", match_room.title);

		//Get path that matches first exit and the correct roomtype
		var match_paths = rd_filter_paths_by_start_and_roomtype(
			match_room,  
			first_path.exitdoor.type, 
			rd_get_opposite_dir(first_path.exitdoor.dir), 
			pathtimes, 
			roomtypes
			);
		
		ds_list_add(stored_match_paths, match_paths);
		ds_list_mark_as_list(stored_match_paths, mr); //auto delete sublists
		
		//var tried = false;
		
		for (var mp = 0; mp < ds_list_size(match_paths); mp++)
		{
			var match_path = ds_list_find_value(match_paths, mp);
			var exitpair = rd_get_exit_struct(match_path);
			
			var temp3 = global.test_string;
			global.test_string = concat(global.test_string, " ", match_path.startdoor.letter, " ", match_path.exitdoor.letter, " -> ", last_room.title);
			
			//TODO: didnt try ruin_8 despite it having new kinds of exits
			//Dont try exits that were tested this direct connection loop OR previously tested in this connection
			if (rd_list_contains_exit(global.connection_tested_exits, exitpair) 
			|| rd_list_contains_exit(temp_used_exits, exitpair)) //Skip path exits that have already been tested directly
				continue;
			
			//tried = true;
			
			ds_list_add(temp_used_exits, exitpair);
			
			var new_connection = rd_connect_directly(
				match_room, match_path, last_room, roomtypes, pathtimes, 
				last_start_letter, last_exit_letter, 
				use_last_start, use_last_exit, 
				use_branch_start, use_branch_exit);
			
			if (new_connection != undefined)
			{
				var connection_to_first =
				{
					first: first_room,
					path: first_path,
					second: new_connection
				};
				
				return connection_to_first;
			}
				
			global.test_string = temp3;
			//Try next match path
		}
		
		//if (!tried)
			//show_debug_message( concat("Didn't try any paths from ", match_room.title) );
		
		global.test_string = temp;
		//Try next match room
	}
	
	ds_list_destroy(temp_used_exits);
	
	//Try to find a match room that connects to last with a new room inbetween
	for (var mr = 0; mr < ds_list_size(match_rooms); mr++) 
	{
		var match_room = ds_list_find_value(match_rooms, mr);
		
		var temp = global.test_string;
		global.test_string = concat(global.test_string, " -> recursive ", match_room.title);
		
		var match_room = ds_list_find_value(match_rooms, mr);
		var match_paths = ds_list_find_value(stored_match_paths, mr);
		
		//Don't reuse later in the connection
		//If its not used, its exits cannot possibly connect to last, so dont remove it
		ds_map_add(global.connection_tested_rooms, match_room.title, match_room); 
		
		//Test every path of that room
		for (var mp = 0; mp < ds_list_size(match_paths); mp++)
		{
			var match_path = ds_list_find_value(match_paths, mp);
			var exitpair = rd_get_exit_struct(match_path);
			
			var temp2 = global.test_string;
			global.test_string = concat(global.test_string, " ", match_path.startdoor.letter, " ", match_path.exitdoor.letter);
			
			if (rd_list_contains_exit(global.connection_tested_exits, exitpair))
				continue;
						
			ds_list_add(global.connection_tested_exits, exitpair);
			
			var incomplete_connection = 
			{
				first: match_room,
				path: match_path,
				second: undefined
			};
				
			//recursive call with a new room on the end
			var next_connection = rd_find_connections(
				incomplete_connection, 
				last_room, 
				roomtypes, 
				pathtimes, 
				last_start_letter, last_exit_letter, 
				use_last_start, use_last_exit,
				use_branch_start, use_branch_exit);

			//valid found, return it //TODO: why are we checking if next connection.second is also not undefined?
			//May be because next_connection.second should be a connection to last and not undefined

			if (next_connection != undefined && next_connection.second != undefined) //a valid connection was found
			{
				connection.second = next_connection;
				return connection;
			}
			
			global.test_string = temp2;
				
		}

		//Try next match room
		global.test_string = temp;
	}
	
	//Exhausted all match rooms
	return undefined;
}

function rd_connect_directly(first_room, first_path, last_room, roomtypes, pathtimes, 
last_start_letter, last_exit_letter, use_last_start, use_last_exit, 
use_branch_start = false, use_branch_exit = false)
{
	if (first_room.title == global.first_test_name && last_room.title == global.test_name)
	{
		show_debug_message( concat("Connecting directly for ", first_room.title, " and path ", first_path, " to ", last_room.title) );
		show_debug_message( concat("Using branch start? exit? ", use_branch_start, " and  ", use_branch_exit) );
	}
	
	var potential_last_paths = rd_filter_paths_by_start_and_roomtype(
		last_room, 
		first_path.exitdoor.type, 
		rd_get_opposite_dir(first_path.exitdoor.dir), 
		pathtimes,
		roomtypes,
		"",
		use_branch_start, use_branch_exit);
	
	var last_paths = ds_list_create();
	
	//Determine which paths have valid letters/is branch
	for (var plp = 0; plp < ds_list_size(potential_last_paths); plp++)
	{
		var potential_last_path = ds_list_find_value(potential_last_paths, plp);
		
		var correct_start = last_start_letter = "" || (use_last_start && potential_last_path.startdoor.letter == last_start_letter) || (!use_last_start && potential_last_path.startdoor.letter != last_start_letter);
		var correct_exit = last_exit_letter = "" || (use_last_exit && potential_last_path.exitdoor.letter == last_exit_letter) || (!use_last_exit && potential_last_path.exitdoor.letter != last_exit_letter);
	
		//its okay if its not marked branch if we're connecting to a john room which wont have a door marked branch
		var correct_branch_start = ( !use_branch_start || (use_branch_start && potential_last_path.startdoor.branch) );
		var correct_branch_exit = ( !use_branch_exit || (use_branch_exit && potential_last_path.exitdoor.branch) )
		var correct_branch = (correct_branch_start && correct_branch_exit) || last_room.roomtype == roomtype.john || last_room.roomtype == roomtype.johnbranching;
	
		if (first_room.title == global.first_test_name && last_room.title == global.test_name)
		{
			show_debug_message( concat("Testing direct for path ", potential_last_path) );
			show_debug_message( concat("start? exit? branch? ", correct_start, ", ", correct_exit, ", ", correct_branch) );
		}
	
		if (correct_start && correct_exit && correct_branch)
		{
			ds_list_add(last_paths, potential_last_path);
			break; //Only one path is used
		}
	}
	
	var size = ds_list_size(potential_last_paths);
	ds_list_destroy(potential_last_paths);

	//If there is at least one valid path
	if (ds_list_size(last_paths) > 0 )
	{
		var last_path = ds_list_find_value(last_paths, 0);

		show_debug_message( concat(rd_buffer(), global.test_string, " ", last_path.startdoor.letter) );

		var connection_last = 
		{
			first: last_room,
			path: last_path, //Not used for linking BUT the start is used as reference when creating the next sequence
			second: undefined //Indicates that it is the end of the connection
		};
							
		var connection_to_first =
		{
			first: first_room,
			path: first_path,
			second: connection_last
		};
		
		ds_list_destroy(last_paths);
		
		//Found a route from first to last
		return connection_to_first;
	}
	
	show_debug_message( concat(rd_buffer(), global.test_string, " NONE PLP size: ", size ) );

	ds_list_destroy(last_paths);
	return undefined;
}

//Go through all connections in the sequences and add them to the transition map
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

//Go through every room and path in the connections and add them to the transition map
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

//Take two rooms and a path and add them to the transition map by ID
function rd_add_path_with_room(from_room, from_path, to_room, to_path)
{
	//Fix duplicated rooms to use the actual ID
	var from_extra = string_pos("_SECOND", from_room.title);
	
	if (from_extra == 0)
		from_extra = string_pos("_THIRD_", from_room.title);
		
	
	var to_extra = string_pos("_SECOND", to_room.title);
	
	if (to_extra == 0)
		to_extra = string_pos("_THIRD_", to_room.title);
	
	var real_from_title = from_extra != 0 ? string_delete(from_room.title, from_extra, 7) : from_room.title;
	var real_to_title = to_extra != 0 ? string_delete(to_room.title, to_extra, 7) : to_room.title;
	
	var from_ID = asset_get_index(real_from_title);
	var to_ID = asset_get_index(real_to_title);
	
	if (from_ID == -1 || to_ID == -1)
	{
		show_debug_message( concat("invalid room ID for ", from_room.title, " or ", to_room.title) );
	}
		
	
	var from_letter = from_path.exitdoor.letter;
	var to_letter = to_path.startdoor.letter;
		
	show_debug_message(concat("connected ", from_room.title, " ", from_letter, " to ", to_room.title, " ", to_letter));
	

	rd_add_path(from_ID, from_letter, to_ID, to_letter);
	
	//TODO: unnecessary? we're already filtering out all_rooms during construction then deleting it later
	rd_remove_room(from_room);
	rd_remove_room(to_room);
}

//Take two IDs and two Letters and add it to the transition map forwards and backwards
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
function rd_filter_paths(from_room, desired_type, desired_dir, desired_times, desired_letter, start)
{
	if (from_room.title == global.test_name)
		show_debug_message( concat("filter paths for ", from_room.title) );
	
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
			p_type = path.startdoor.type;
			p_dir = path.startdoor.dir;
			p_letter = path.startdoor.letter;
		}
		else
		{
			p_type = path.exitdoor.type;
			p_dir = path.exitdoor.dir;
			p_letter = path.exitdoor.letter;
		}
		
		var time_matches = false;
		
		if (! is_array(desired_times) )
			desired_times = [desired_times];
		
		for (var j = 0; j < array_length(desired_times); j++)
		{
			if (from_room.title == global.test_name)
				show_debug_message( concat("Time wanted: ", desired_times[j]) );
				
			if (p_time == desired_times[j])
			{
				time_matches = true;
				break;
			}
		}
		
		if (array_contains(desired_times, pathtime.none) )
			time_matches = true;
				
		if (	time_matches
			&& (p_type == desired_type || desired_type == transition.none)
			&& (p_letter == desired_letter || desired_letter == "")
			&& (p_dir == desired_dir || desired_dir == transitiondir.none)
			)
			{
				ds_list_add(valid_paths, path);
				
				if (from_room.title ==  global.test_name)
					show_debug_message( concat("Good path for ", from_room.title, " ", path) );
			}
		else
		{
			if (from_room.title ==  global.test_name)
					show_debug_message( concat("Bad path for ", from_room.title, " ", path) );
		}
		
		if (from_room.title ==  global.test_name)
		{
			show_debug_message( concat("test filtering: ", path) );
			
			var kind = start ? "start" : "exit";
			
			if (!time_matches)
				show_debug_message( concat("above ", kind, " time does not match: ", desired_times) );
			
			if (! (p_type == desired_type || desired_type == transition.none))
				show_debug_message( concat("above ", kind, " type does not match: ", desired_type) );
			
			if (! (p_letter == desired_letter || desired_letter == ""))
				show_debug_message( concat("above ", kind, " letter does not match: ", desired_letter) );
			
			if (! (p_dir == desired_dir || desired_dir == transitiondir.none) )
				show_debug_message( concat("above ", kind, " dir does not match: ", desired_dir) );
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
		
		if (array_contains(roomtypes_arr, thisroom.roomtype ) )
			ds_list_add(potential_rooms, thisroom);
			
	}
	
	ds_list_shuffle(potential_rooms);

	if (ds_list_size(potential_rooms) == 0)
		show_debug_message( concat("NO ROOMS OF TYPES ", roomtypes_arr) );
	
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
