"""
This module contains the WifiCommands class.
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=protected-access
from time import sleep
from hardware_manager import HwMan
from wireless_tools.wlan import WlanManager
from commands.commands_dispatcher import CommandsDispatcher


class WifiCommands(CommandsDispatcher):
    """
    This class is used to manage wifi commands.
    """
    def __init__(self):
        self.pages_manager = super.pages_manager
        self.commands = super.commands
        self.wlan = WlanManager()
        self.hw_man = HwMan

    def exec(self, page_cursor_key: tuple) -> None:
        """
        This method is used to execute the commands.
        - Args:
            - page_cursor_key: a tuple containing the page id
                and the cursor position.
        """
        if page_cursor_key[0] != 5:
            if self.commands[page_cursor_key] == "wlan scan":
                self.__wlan_scan()
            elif self.commands[page_cursor_key] == "wlan status":
                self.__wlan_status()
        elif (
            self.commands[page_cursor_key[0]]
                == "wlan insert password"):
            self.__wlan_insert_password(page_cursor_key[1])

    def __wlan_scan(self):
        HwMan.oled.fill(0)
        HwMan.oled.text("scanning...", 0, 0)
        HwMan.oled.show()
        command_output = self.wlan.scan()
        self.wlan.saved_ssids = command_output["ssids"]
        entries = []
        for i in range(len(command_output["ssids"])):
            entries.append(
                command_output["ssids"][i][0:8]+" "
                + str(command_output["rssi"][i])
            )
        entries.append("back")
        self.pages_manager.add_page(
            page_id=5,
            is_leaf=True,
            entries=entries
        )
        self.pages_manager.target_page = self.pages_manager.pages[-1]
        self.pages_manager.__display_page()

    def __wlan_status(self):
        HwMan.oled.fill(0)
        connected = self.wlan.status()["isconnected"]
        conn_data = self.wlan.status()["ifconfig"]
        if connected:
            HwMan.oled.text("wlan connected", 0, 0)
            HwMan.oled.text("ip:"+conn_data[0], 0, 11)
            HwMan.oled.text("msk:"+conn_data[1], 0, 22)
            HwMan.oled.text("gate:"+conn_data[2], 0, 33)
            HwMan.oled.show()
            timer = 5
            while timer > 0:
                HwMan.oled.fill_rect(0, 44, 128, 8, 0)
                HwMan.oled.text("homepage in"+str(timer)+"...", 0, 44)
                HwMan.oled.show()
                sleep(1)
                timer -= 1
            self.pages_manager.target_page = self.pages_manager.pages[0]
            self.pages_manager.__display_page()
        else:
            HwMan.oled.text("wlan not connected", 0, 0)
            timer = 5
            while timer > 0:
                HwMan.oled.fill_rect(0, 44, 128, 8, 0)
                HwMan.oled.text("homepage in"+str(timer)+"...", 0, 44)
                HwMan.oled.show()
                sleep(1)
                timer -= 1
            self.pages_manager.target_page = self.pages_manager.pages[0]
            self.pages_manager.__display_page()

    def __wlan_insert_password(self, pc_key):
        self.pages_manager.destroy_last_page()
        password = HwMan.write_from_keyboard_to_oled()
        if password is not None:
            isconnected = self.wlan.connect(
                self.wlan.saved_ssids[pc_key],
                password
            )
            if isconnected:
                HwMan.oled.fill(0)
                HwMan.oled.text("connected!", 0, 0)
                HwMan.oled.show()
                sleep(2)
                self.pages_manager.target_page = self.pages_manager.pages[0]
                self.pages_manager.__display_page()
            else:
                HwMan.oled.fill(0)
                HwMan.oled.text("failed!", 0, 0)
                HwMan.oled.show()
                sleep(2)
                self.pages_manager.target_page = self.pages_manager.pages[0]
                self.pages_manager.__display_page()
