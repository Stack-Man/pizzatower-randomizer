enum roomtype
{
	oneway,
	twoway,
	potentialoneway,
	branching,
	entrance,
	john,
	entrancebranching,
	johnbranching,
	ratblockedtwoway,
	potentialratblockedtwoway,
	loop
}

enum pathtime
{
	any, //both pt and npt
	pizzatime,
	notpizzatime,
	none //pt, npt, or any
}

enum transition
{
	hallway,
	vertical,
	horizontal,
	door,
	box,
	secret,
	none
}

enum transitiondir
{
	up,
	down,
	left,
	right,
	none
}

enum pathvalues
{
	startletter,
	exitletter,
	starttype,
	exittype,
	startdir,
	exitdir,
	pathtime
}

enum roomvalues
{
	title,
	type,
	paths,
	special
}

enum levelvalues
{
	entrance, 
	john, 
	branches, 
	initialbranches,
}

enum validpathvalues
{
	title,
	type,
	validpaths
}

enum destinationvalues
{
	roomid,
	letter
}


//Parsed Rooms Map
//roomtype : Parsed Room Map

//Parsed Room Map
//roomvalues.title : string
//roomvalues.paths : Paths List
//roomvalues.type : roomtype

//Paths List
//Path Map

//Path Map
//pathvalues.startletter : string
//pathvalues.exitletter : string
//pathvalues.startype : transition
//pathvalues.endtype : transition
//pathvalues.startdir : transitiondir
//pathvalues.enddir : transitiondir
//pathvalues.pathtime : pathtime

//Levels Map
//string level name : Level Map

//Level Map
//levelvalues.entranceroom : Section Map
//levelvalues.johnroom : Section Map
//levelvalues.branchingrooms : list of Section Maps
//levelvalues.returnsections : Array of Section Maps
//levelvalues.totalbranchingrooms : int
