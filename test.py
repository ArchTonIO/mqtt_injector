from hardware_manager import HardwareManager
from pages_manager import PagesManager

hw = HardwareManager()
pm = PagesManager(hw.encoder, hw.select_button, hw.oled)

pm.build_menu_from_json("settings/pages.json")
pm.loop()
