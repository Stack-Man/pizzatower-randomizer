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
	var versionstr = "RANDOMIZER V0.1";
	draw_text(8, 8, versionstr);
}