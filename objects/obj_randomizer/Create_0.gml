depth = -6000;

//TODO:
//dungeon_4 can only start notpizzatime but can exit pizzatime

//plage_shipmain has loop to itself between different doors and weird door setup
//forest_G1 has loop to itself between different doors
//trickytreat_1 resets the level state when entering it
//medievakl_6 softlocks if you pick up the knight powerup and go down the slope

//Ignore the shared rooms in CTOP and main level for now, add transition map exception later

//noise keeps jetpack
//gustavo persist with swap mode

//TODO: consistently makes 20 out of 21 levels
//may be that allow_to.. isnt also checking for branchany when allowing a notpizzatime path, but adding this makes it fail a lot
//supposeduly because its activating when its not supposed to then

//loading
version = "0.3";
validversion = true;
loadedjson = false;
loadedini = false;
global.missing_json = 0;
global.outdated_json = false;
global.room_msg = "";

//separating level construction across multiple frames
war_exit_used = false;
all_entrances = undefined;
current_entrance_index = 0;
all_levels = undefined;
current_level_index = 0;
levels_failed_to_add = undefined;
add_exhaustive = false;

//Progression
global.levels_beat = 0;
global.beat_all_levels = false;
global.total_levels = 4;

//logging
global.recursion_depth = 0;
global.test_string = "";
global.log = "";

//TODO: ini file these
global.use_loops = false;
max_branches = 2;
max_rooms = 10;

ignore_rooms = [
"forest_G1", "plage_shipmain", "dungeon_4",
"tower_1", "tower_johngutterhall", "tower_2", "tower_3", "tower_4", "tower_5",
"tower_tutorial1N", "trickytreat_1", 
"medieval_6"];

global.boss_levels = [boss_pepperman, boss_vigilante, boss_noise, boss_fakepep, boss_pizzaface];

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

saved_hsp = 0;
saved_movespeed = 0;
current_powerup = poweruptype.none;

alarm[3] = 70; //generate