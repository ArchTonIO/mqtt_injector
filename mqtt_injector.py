from pages_manager import pages_manager
from hardware_manager import h_man

class mqtt_injector():
	def __init__(self):

		self.pages_manager=pages_manager(h_man.oled,
											h_man.encoder,
											h_man.select_button)
		self.pages_manager.add_page(page_id=0,
									entries=["wlan_tools",
									"mqtt_tools",
									"sensors",
									"config",
									"hardware_check",
									"back",
									"screen off"])
		self.pages_manager.add_page(page_id=1,
									leaf_attr=True,
									entries=["wlan status",
									"wlan connect",
									"wlan scan",
									"back"])
		self.pages_manager.add_page(page_id=2,
									leaf_attr=True,
									entries=["mqtt status",
									"mqtt set_broker",
									"mqtt subscribe",
									"mqtt publish",
									"back"])
		self.pages_manager.add_page(page_id=3,
									leaf_attr=True, 
									entries=["slot 1",
									"slot 2",
									"slot 3",
									"slot 4",
									"slot 5",
									"back"])
		self.pages_manager.add_page(page_id=4,
									leaf_attr=True,
									entries=["save config",
									"load config",
									"read log",
									"back"])
		self.pages_manager.loop()

device=mqtt_injector()