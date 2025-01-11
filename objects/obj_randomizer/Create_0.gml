depth = -6000;

current_powerup = poweruptype.none;

global.first_test_name = "test";
global.test_name = "test";

global.recursion_depth = 0;
global.test_string = "";

global.use_loops = false;

ignore_rooms = ["forest_G1", "plage_shipmain", "minigolf_8", "minigolf_4", "space_9", "forest_G5", "farm_1", "kidsparty_floor4_3"];
separated_rooms = ["ruin_11", "badlands_5", "industrial_2", "industrial_3", "industrial_4"]; //TODO: implement

//kidsparty_floor4_3 is branching room but entirely different branch entrance from branch exit, it would need to be in the middle of another branch
//farm_1 is branching room but the branch entrance is exitonly
//forest G5 branching room but the branch entrance is a oneway, need to let it exist int he middle of another branch
//ruin_8 branching but pizzatime entrance is a startonly instead
//freezer_13 branching but pizzatime entrance is a startonly instead
//space_9 needs ROCKET entrance
//minigolf_4 not branching but pizzatime gerome makes it count
//plage_shipmain has loop to itself between different doors and weird door setup
//forest_G1 has loop to itself between different doors

//TODO: add trickytreat and handling since it doesnt have an entrance or john
level_names = [ 
//"tutorial", "tutorial_noise", //"trickytreat",
"johngutter", "pizzascape", "bloodsauce", "ancientcheese", 
"wasteyard", "funfarm", "oreganodesert",  
"gnomeforest", "golf", "crustcove", //"deepdish9",
"freezer", "ohshit", "peppibotfactory", "thepigcity",
"dontmakeasound", "pizzascare", "war"
];

twoway_types = [roomtype.twoway, roomtype.potentialoneway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];
oneway_types = [roomtype.oneway, roomtype.potentialoneway, roomtype.twoway, roomtype.ratblockedtwoway, roomtype.potentialratblockedtwoway];

rd_generate_new();