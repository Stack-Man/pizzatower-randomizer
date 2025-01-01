/// @description Insert description here
// You can write your code in this editor
randomize();
room_id_went_to = 0;
seed = 0;
level_names = ["johngutter", "pizzascape", "bloodsauce", "funfarm", "ancientcheese", "tutorial", "tutorial_noise"];

twoway_types = [roomtype.twoway, roomtype.potentialoneway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];
oneway_types = [roomtype.oneway, roomtype.potentialoneway, roomtype.twoway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];

global.sequence_tested_rooms = ds_map_create(); //Doesn't get cleared between sequences
global.connection_tested_rooms = ds_map_create(); //Does get cleared whenever calling rd_connect_rooms_with_type_start
global.connection_tested_exits = ds_list_create(); //same as above

global.all_rooms = rd_parse_rooms();
global.transition_map = ds_map_create();
global.powerup_map = ds_map_create();
rd_construct_levels();

ds_map_destroy(global.all_rooms);
ds_map_destroy(global.connection_tested_rooms);
ds_map_destroy(global.sequence_tested_rooms);
ds_list_destroy(global.connection_tested_exits);