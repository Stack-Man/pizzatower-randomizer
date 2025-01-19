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
		
	draw_text(8, 24, seedstr);
	
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