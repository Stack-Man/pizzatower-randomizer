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
	

}