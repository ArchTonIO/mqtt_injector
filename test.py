""" Temporary test file. """
import _thread
from time import sleep

from commands_dispatcher import CommandsDispatcher
from hardware_manager import HardwareManager
import logger
from pages_manager import PagesManager
from settings_manager import SettingsManager
import _thread

hw_man = HardwareManager()
# _thread.start_new_thread(hw_man.startup_sequence, ())

logger.init()
SettingsManager.load_settings("settings")
menu_pages = SettingsManager.get_settings("pages")

cmd_disp = CommandsDispatcher(hw_man)
p_man = PagesManager(
    hw_man.encoder,
    hw_man.select_button,
    hw_man.oled,
    cmd_disp
)

p_man.build_menu_from_dict(menu_pages)


p_man.run(recovery_from_exceptions=False)
