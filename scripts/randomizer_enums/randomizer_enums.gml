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

enum poweruptype
{
	none,
	gustavo,
	shotgun,
	barrel,
	satan
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
//startletter : string
//exitletter : string
//startype : transition
//endtype : transition
//startdir : transitiondir
//enddir : transitiondir
//pathtime : pathtime
//exitdoor : exit door struct
//startdoor : start door struct

//Start Door Struct
//startonly : start only
//ratblocked : rat blocked

//Exit Door Struct
//exitonly : exit only
//ratblocked : rat blocked

//Destination Struct
//roomid : room index
//letter : string