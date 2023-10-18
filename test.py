""" Temporary test file. """

from pages_manager import PagesManager
from hardware_manager import HardwareManager
from commands_dispatcher import CommandsDispatcher

hw_man = HardwareManager()
cmd_disp = CommandsDispatcher(hw_man)
p_man = PagesManager(
    hw_man.encoder,
    hw_man.select_button,
    hw_man.oled,
    cmd_disp
)

p_man.build_menu_from_json("settings/pages.json")
p_man.run()
