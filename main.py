from hardware_manager import h_man
from pages_manager import pages_manager
import _thread

_thread.start_new_thread(h_man.startup_sequence, ())
#h_man.startup_sequence()
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
					"screen off"
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
					"fast publish"
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