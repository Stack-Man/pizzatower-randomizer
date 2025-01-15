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
	loop,
	branchstart, //must initially enter with branch door
	branchend, //must initially exit with branch door
	branchany, //can either enter or exit with branch door
	branchmid, //must be inbetween two branches, enter branchstart during notpizzatime and exit branchexit during pizzatime
	warexit,
	ctopexit,
	ctopentrance
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
	vertical,
	horizontal,
	door,
	box,
	secret,
	rocket,
	taxi,
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

enum poweruptype
{
	none,
	gustavo,
	shotgun,
	barrel,
	satan,
	ghostking
}


//Parsed Rooms Map
//roomtype : Parsed Room Map

//Parsed Room Struct
//title : string
//paths : Paths List
//roomtype : roomtype

//Paths List
//Path Struct

//Path Struct
//pathtime : pathtime
//exitdoor : exit door struct
//startdoor : start door struct
//oneway

//Start Door Struct
//startonly : start only
//ratblocked : rat blocked
//branch
//exitdoor
//branchstart
//branchexit
//letter : string
//dir : transitiondir enum
//type : transition enum
//loop

//Exit Door Struct
//exitonly : exit only
//ratblocked : rat blocked
//branch
//exitdoor
//branchstart
//branchexit
//letter : string
//dir : transitiondir enum
//type : transition enum
//loop

//Destination Struct
//roomid : room index
//letter : string