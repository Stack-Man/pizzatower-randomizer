/// @description Create key/gerome if necessary

if (instance_exists(obj_keydoor))
{
	var create = false;
	
	with (obj_keydoor)
	{
		create = sprite_index != spr_doorkeyopen;
	}
	
	if (create)
		rd_key(true);
}
else
{
	rd_key(false);
}

if (instance_exists(obj_geromedoor))
{
	var create = false;
	
	with (obj_geromedoor)
	{
		create = sprite_index != spr_gerome_opendoor;;
	}
	
	if (create)
		rd_gerome(true);
}
else
{
	rd_gerome(false);
}
