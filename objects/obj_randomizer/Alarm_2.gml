// @description delete bad door

//Delete crashing door that may appear in some rooms, such as pizzascape's gerome door
with (obj_door)
{
	if ( !variable_instance_exists(self, "targetRoom") )
		instance_destroy(self);
}