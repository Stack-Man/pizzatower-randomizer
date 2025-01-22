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

}