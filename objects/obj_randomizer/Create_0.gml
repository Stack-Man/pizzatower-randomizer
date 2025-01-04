depth = -6000;

global.use_loops = false;

ignore_rooms = ["forest_G1"];
separated_rooms = ["ruin_11"];
level_names = [ 
"tutorial", "tutorial_noise", 
"johngutter", "pizzascape", "bloodsauce", "ancientcheese", 
"wasteyard", "funfarm",  
"gnomeforest", "golf", "crustcove",
"freezer"];

twoway_types = [roomtype.twoway, roomtype.potentialoneway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];
oneway_types = [roomtype.oneway, roomtype.potentialoneway, roomtype.twoway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];

rd_generate_new();