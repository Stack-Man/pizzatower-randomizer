/// @description Create One Level
// You can write your code in this editor

var first_room = ds_list_find_value(all_entrances, current_entrance_index);
rd_create_level(first_room);

current_entrance_index++;

if (current_entrance_index < ds_list_size(all_entrances) )
{
	alarm[5] = 1;
}
else
{
	//remember actually used rooms 
	for (var k = 0; k < ds_list_size(all_levels); k++)
	{
		var level = ds_list_find_value(all_levels, k);
		rd_add_sequence_rooms_to_map(level, global.sequence_used_rooms); 
	}
	
	levels_failed_to_add = ds_list_create(); //TODO : destroy list
	
	alarm[6] = 1;
}