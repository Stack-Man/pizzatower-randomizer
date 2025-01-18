depth = -6000;
version = "0.1";
validversion = true;
loadedjson = false;
loadedini = false;

current_powerup = poweruptype.none;
global.print_connection_debug = true;

global.first_test_name = "badland_5_3";
global.test_name = "kidsparty_floor1_3";

global.recursion_depth = 0;
global.test_string = "";

global.use_loops = false;
max_branches = 2;
max_rooms = 10;

ignore_rooms = [
"forest_G1", "plage_shipmain", 
"tower_1", "tower_johngutterhall", "tower_2", "tower_3", "tower_4", "tower_5", "ruin_11",
"tower_tutorial1N", "trickytreat_1", 
"medieval_6"];

global.boss_levels = [boss_pepperman, boss_vigilante, boss_noise, boss_fakepep, boss_pizzaface];

//TODO:
//TODO: some rooms are not being treated as branches
//scr_room_goto is interupting reset level and forcing you to the previous room instead

//chateau 7 not being used as a branch? farm_4 also

//gustavo/peppino door skips door exit naimation
//gustavo to peppino causes velocity in the wrong direction
//modify scr_switchpep/gus to not reset state

//taxi does not work, problem wiht door being set

//restart is broken
//ctop only ever gets 3 rooms

//space_9 always failing, rocket doors and taxi doors may not work properly, now farm_2 failed, so its something else, a lack of johns?

//floor progression since toppins are a no go (always give $50 for every level? require beating all or X levels?)
//fix gustavo door/transition messuips, save door state and duirection then set them after doing the switch?

//minigolf_8 has the loop to itself
//plage_shipmain has loop to itself between different doors and weird door setup
//forest_G1 has loop to itself between different doors
//trickytreat_1 resets the level state when entering it
//medievakl_6 softlocks if you pick up the knight powerup and go down the slope

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