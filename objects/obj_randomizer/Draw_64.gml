/// @description Insert description here
// You can write your code in this editor
if variable_global_exists("smallfont")
{
	draw_set_font(global.smallfont);
	draw_set_alpha(1);
	draw_set_color(c_white);
	draw_set_halign(fa_left);
	draw_set_valign(fa_top);
	
	//Draw Version
	var versionstr = concat("RD V", version);
	draw_text(8, 0, versionstr);
	
	var seedstr = seed;
	
	if (seed < 0)
		seedstr = concat("M", seedstr);
	
	if (!loadedjson)
	{
		seedstr = concat("NEW ", seedstr);
		
		if (!loadedini)
			seedstr = concat("NO INI ", seedstr);
	}	
	else
	{
		seedstr = concat("LOADED ", seedstr);
		
		if (!validversion)
			seedstr = concat("MISMATCHED VERSION ", seedstr);
	}
	
	if (global.missing_json <= 0)
		draw_text(8, 24, seedstr);
	else
	{
		draw_set_font(-1);
		draw_text(8, 24, concat("MISSING ", global.missing_json," JSON FILES IN ", working_directory, "json") );
		draw_set_font(global.smallfont);
	}
	
	if (global.outdated_json)
	{
		draw_text(8, 48, "OUTDATED JSON");
	}
	
	draw_set_font(-1);
	draw_text(8, 48 + 24, global.room_msg);
	draw_set_font(global.smallfont);
	
	/*with (obj_player1)
	{
		draw_set_font(global.smallfont);
		
		var hallwaystr = hallwaydirection;
		
		if (hallwaydirection < 0)
			hallwaystr = concat("M", hallwaystr);
			
		var truestr = global.true_direction;
	
		if (truestr < 0)
			truestr = concat("M", truestr);
		
		var vals = concat("HALLWAY: ", hallway, " DIR: ", hallwaystr, " TRUE: ", truestr, " BOX: ", box, " TARGET: ", targetDoor);
		var target = concat("X: ", global.door_x, " OFFSET: ", global.door_x_offset, " Y: ", global.door_y);
		
		draw_text(8, 48 + 24 + 24, vals);
		draw_text(8, 48 + 48 + 24, target);
	}*/
	
	/*with (obj_player1)
	{
		draw_text(8, 48, state);
		
		if (variable_instance_exists(self, "ratmount_movespeed"))
		{
			var spdstr = ratmount_movespeed;
			
			if (ratmount_movespeed < 0)
				spdstr = concat("M", spdstr);
			
			draw_text(8, 48 + 24, concat("RSP: ", spdstr));
			
			var hspstr = hsp;
			var vspstr = vsp;
			
			if (hsp < 0)
				hspstr = concat("M", hspstr);
			
			if (vsp < 0)
				vspstr = concat("M", vspstr);
				
			draw_text(8, 48 + 48 , concat("HSP: ", hspstr) );
			draw_text(8, 48 + 48 + 24, concat("VSP: ", vspstr) );
			
			
			var mspstr = movespeed;
			if (movespeed < 0)
				mspstr = concat("M", mspstr);
			
			draw_text(8, 48 + 48 + 24 + 24, concat("MSP: ", mspstr) );
		}
	}*/
	

}