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

//Destination Struct
//roomid : room index
//letter : string