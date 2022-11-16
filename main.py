from hardware_manager import h_man
from pages_manager import pages_manager

try:
	h_man.startup_sequence()
	pages_man=pages_manager(
						h_man.oled,
						h_man.encoder,
						h_man.select_button
						)
	pages_man.add_page(page_id=0,
						entries=[
						"wlan tools",
						"ble tools",
						"mqtt tools",
						"sd card tools",
						"config",
						"hardware check",
						"screen off",
						"back"
						])
	pages_man.add_page(page_id=1,
						leaf_attr=True,
						entries=[
						"wlan scan",
						"wlan status",
						"wlan connect",
						"back"
						])
	pages_man.add_page(page_id=2,
						leaf_attr=True,
						entries=[
						"ble status",
						"ble scan",
						"ble connect",
						"back"
						])
	pages_man.add_page(page_id=3,
						leaf_attr=True,
						entries=[
						"mqtt status",
						"mqtt set brokr",
						"mqtt subscribe",
						"mqtt publish",
						"fast publish",
						"back"
						])
	pages_man.add_page(page_id=4,
						leaf_attr=True, 
						entries=[
						"mount card",
						"umount card",
						"read log",
						"write code",
						"excecute code",
						"navigate fs",
						"back"
						])
	pages_man.add_page(page_id=5,
						leaf_attr=True,
						entries=[
						"boot hw check",
						"boot animation",
						"error recovery",
						"led brightness",
						"oled brightnes",
						"oled contrast",
						"rverse encoder",
						"save to flash",
						"available sram",
						"availble flash",
						"back"
						])
	pages_man.loop()
except Exception as e:
	h_man.oled.fill(0)
	h_man.oled.text("[FATAL ERROR]", 8, 0)
	error_str=str(e)
	col_c=0
	raw_c=30
	for i in range(len(error_str)):
		h_man.oled.text(error_str[i], col_c, raw_c)
		col_c+=8
		if col_c>120:
			col_c=0
			raw_c+=10
	h_man.oled.show()