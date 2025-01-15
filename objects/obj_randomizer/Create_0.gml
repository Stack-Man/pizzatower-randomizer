depth = -6000;

current_powerup = poweruptype.none;


global.first_test_name = "test";
global.test_name = "test";

global.created_levels = ds_list_create();

global.recursion_depth = 0;
global.test_string = "";

global.use_loops = false;
max_branches = 2;

ignore_rooms = [
"forest_G1", "plage_shipmain", 
"tower_1", "tower_johngutterhall", "tower_2", "tower_3", "tower_4", "tower_5", "ruin_11",
"tower_tutorial1N"];

global.boss_levels = [boss_pepperman, boss_vigilante, boss_noise, boss_fakepep, boss_pizzaface];

//TODO:
//gustavo/peppino door skips door exit naimation
//gustavo to peppino causes velocity in the wrong direction

//control how many rooms are being added to levls

//restart is broken

//space_9 always failing, rocket doors and taxi doors may not work properly, now farm_2 failed, so its something else, a lack of johns?

//create direct room handling for crumbling tower

//floor progression since toppins are a no go (always give $50 for every level? require beating all or X levels?)
//fix gustavo door/transition messuips, save door state and duirection then set them after doing the switch?

//minigolf_8 has the loop to itself
//plage_shipmain has loop to itself between different doors and weird door setup
//forest_G1 has loop to itself between different doors

//Ignore the shared rooms in CTOP and main level for now, add transition map exception later
//ignore tower tutorial1N cause whatever bro

level_names = [ 
"tutorial", "tutorial_noise", "trickytreat",
"johngutter", "pizzascape", "bloodsauce", "ancientcheese", 
"wasteyard", "funfarm", "oreganodesert", "fastfoodsaloon",
"gnomeforest", "golf", "crustcove", "deepdish9",
"freezer", "ohshit", "peppibotfactory", "thepigcity",
"dontmakeasound", "pizzascare", "war", "crumblingtowerofpizza"
];

twoway_types = [roomtype.twoway, roomtype.potentialoneway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];
oneway_types = [roomtype.oneway, roomtype.potentialoneway, roomtype.twoway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];

rd_generate_new();