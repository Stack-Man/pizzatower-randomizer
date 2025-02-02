/// @description Pad One Level then finish
// You can write your code in this editor

var level = ds_list_find_value(all_levels, current_level_index);
var rooms_added = 0;

if (ds_list_find_index(levels_failed_to_add, level.last_room.title) == -1)
{	
	var to_add = add_exhaustive ? rd_count_rooms(level) + max_rooms : max_rooms;
	rooms_added = rd_pad_level(level, to_add);
}

current_level_index++;

if (rooms_added == 0)
	ds_list_add(levels_failed_to_add, level.last_room.title);

if (current_level_index < ds_list_size(all_levels) )
{
	alarm[6] = 1;
}
else
{
	//start looping with higher max size
	if (ds_list_size(levels_failed_to_add) < ds_list_size(all_levels) )
	{
		current_level_index = 0;
		add_exhaustive = true;
		
		//TODO: reorder list by size
		alarm[6] = 1;
	}
	else
	{
		//link levels
		rd_link_levels(all_levels);
		var size = ds_list_size(all_levels);
		
		ds_list_destroy(all_levels);

		ds_map_destroy(global.sequence_used_rooms);
		ds_map_destroy(global.all_rooms);
		ds_map_destroy(global.connection_tested_rooms);
		ds_map_destroy(global.sequence_tested_rooms);
		ds_list_destroy(global.connection_tested_exits);
	
		rd_save_seed();
	
		rd_add_to_log( concat("Created ", size, " levels") );
	
		if (variable_global_exists("font_map"))
			create_transformation_tip( concat("Generated ", size, " of ", "21", " levels") );
		
		rd_save_log();
	}
}

