depth = -6000;

current_powerup = poweruptype.none;

global.use_loops = false;

ignore_rooms = ["forest_G1", "plage_shipmain", "minigolf_8"];
separated_rooms = ["ruin_11"];

//TODO: add trickytreat and handling since it doesnt have an entrance or john
level_names = [ 
"tutorial", "tutorial_noise",
"johngutter", "pizzascape", "bloodsauce", "ancientcheese", 
"wasteyard", "funfarm", "oreganodesert",  
"gnomeforest", "golf", "crustcove", "deepdish9",
"freezer", "ohshit", "peppibotfactory", "thepigcity",
"dontmakeasound", "pizzascare", "war"
];

twoway_types = [roomtype.twoway, roomtype.potentialoneway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];
oneway_types = [roomtype.oneway, roomtype.potentialoneway, roomtype.twoway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];

rd_generate_new();