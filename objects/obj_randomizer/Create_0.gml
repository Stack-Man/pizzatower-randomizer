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
"forest_G1", "plage_shipmain", "tower_finalhallway",
"tower_entrancehall", "tower_1", "tower_johngutterhall", "tower_2", "tower_3", "tower_4", "tower_5", "ruin_11",
"tower_tutorial1N"];
separated_rooms = ["ruin_11", "badlands_5", "industrial_2", "industrial_3", "industrial_4", "freezer_9"];

//TODO:

//dont delete boss doors
//rooms added failing still

//space_9 always failing, rocket doors and taxi doosr may not work properly

//ghost king is sometimes persisting, may have to do with natural spawns
//create direct room handling for crumbling tower

//ruin 11 treated like a loop john instead of a branching, entered from door

//separated rooms code not working properly?

//delete unmade levels

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