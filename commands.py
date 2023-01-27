"""
This file contains the commands to be executed when a button is pressed.
"""
# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=no-name-in-module
from time import sleep
from hardware_manager import HwMan
from mqtt_manager import MqttManager
from wireless_tools import WlanManager


class CommandExecuter():
    """
    This class is used to execute the commands.
    """
    def __init__(self):
        self.wlan = WlanManager()
        self.commands = {
            (1, 0): "wlan scan",
            (1, 1): "wlan status",
            (1, 2): "wlan connect",
            5: "wlan insert password",
            (3, 0): "fast publish",
            (3, 1): "fast connect",
            (3, 2): "mqtt set_conn",
            (3, 3): "mqtt connect",
            (3, 4): "mqtt status",
            (3, 5): "mqtt subscribe",
            (3, 6): "mqtt publish",
        }

    def execute(self, pages_manager, target_page, cursor_position):
        """
        This method is used to execute the commands.
        It calls the appropriate method based on the page id.
        - Args:
            - page_cursor_key: a tuple containing the page id
        """
        if (
            target_page == 1
            or cursor_position == 5
        ):
            page_cursor_key = (target_page, cursor_position)
            self.execute_wifi_commands(
                pages_manager,
                page_cursor_key
            )
        elif target_page == 3:
            page_cursor_key = (target_page, cursor_position)
            self.execute_mqtt_commands(
                pages_manager,
                page_cursor_key
            )

    def execute_wifi_commands(
        self,
        pages_manager,
        page_cursor_key: tuple
    ) -> None:
        """
        This method is used to execute the commands.
        - Args:
            - pages_manager: the pages manager object.
            - page_cursor_key: a tuple containing the page id
                and the cursor position.
        """
        try:
            print(
                "executing command:",
                self.commands[page_cursor_key]
            )
        except KeyError:
            print(
                "executing command:",
                self.commands[page_cursor_key[0]]
            )
        if page_cursor_key[0] != 5:
            if self.commands[page_cursor_key] == "wlan scan":
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
                pages_manager.add_page(
                    page_id=5,
                    is_leaf=True,
                    entries=entries
                )
                pages_manager.target_page = pages_manager.pages[-1]
                pages_manager.__display_page()
            elif self.commands[page_cursor_key] == "wlan status":
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
                    pages_manager.target_page = pages_manager.pages[0]
                    pages_manager.__display_page()
                else:
                    HwMan.oled.text("wlan not connected", 0, 0)
                    timer = 5
                    while timer > 0:
                        HwMan.oled.fill_rect(0, 44, 128, 8, 0)
                        HwMan.oled.text("homepage in"+str(timer)+"...", 0, 44)
                        HwMan.oled.show()
                        sleep(1)
                        timer -= 1
                    pages_manager.target_page = pages_manager.pages[0]
                    pages_manager.__display_page()
        elif self.commands[page_cursor_key[0]] == "wlan insert password":
            pages_manager.destroy_last_page()
            password = HwMan.write_from_keyboard_to_oled()
            if password is not None:
                isconnected = self.wlan.connect(
                    self.wlan.saved_ssids[page_cursor_key[1]],
                    password
                )
                if isconnected:
                    HwMan.oled.fill(0)
                    HwMan.oled.text("connected!", 0, 0)
                    HwMan.oled.show()
                    sleep(2)
                    pages_manager.target_page = pages_manager.pages[0]
                    pages_manager.__display_page()
                else:
                    HwMan.oled.fill(0)
                    HwMan.oled.text("failed!", 0, 0)
                    HwMan.oled.show()
                    sleep(2)
                    pages_manager.target_page = pages_manager.pages[0]
                    pages_manager.__display_page()

    def execute_mqtt_commands(
        self,
        pages_manager,
        page_cursor_key: tuple
    ) -> None:
        """
        This method is used to execute the commands
        related to the mqtt client.
        - Args:
            - pages_manager: the pages manager object.
            - page_cursor_key: a tuple containing the page id
                and the cursor position.
        """
        if self.commands[page_cursor_key] == "fast publish":
            MqttManager.fast_publish("sas")
        elif self.commands[page_cursor_key] == "mqtt set_conn":
            MqttManager.broker_ip = HwMan.write_from_keyboard_to_oled(
                initial_text="mqtt broker ip: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
            MqttManager.client_name = HwMan.write_from_keyboard_to_oled(
                initial_text="mqtt client name: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
            MqttManager.keepalive = int(
                HwMan.write_from_keyboard_to_oled(
                    initial_text="mqtt keepalive: ",
                    exit_text="got it!",
                    abort_tex="exiting..."
                )
            )
            MqttManager.create_connection()
        elif self.commands[page_cursor_key] == "fast connect":
            MqttManager.broker_ip = HwMan.write_from_keyboard_to_oled(
                initial_text="mqtt broker ip: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
            MqttManager.broker_ip = "192.168.1.17"
            MqttManager.client_name = "mqtt_injector"
            MqttManager.keepalive = 60
            MqttManager.create_connection()
            MqttManager.connect()
        elif (
                self.commands[page_cursor_key] == "mqtt connect"
                or self.commands[page_cursor_key] == "mqtt status"
        ):
            if self.commands[page_cursor_key] == "mqtt connect":
                MqttManager.connect()
            HwMan.oled.fill(0)
            if MqttManager.status():
                HwMan.oled.text("connected!", 0, 0)
            else:
                HwMan.oled.text("no connection!", 0, 0)
            HwMan.oled.show()
            sleep(2)
            pages_manager.target_page = pages_manager.pages[3]
            pages_manager.__display_page()
        elif self.commands[page_cursor_key] == "mqtt subscribe":
            topic = HwMan.write_from_keyboard_to_oled(
                initial_text="topic: ",
                exit_text="subscribed to {topic}",
                abort_tex="exiting..."
            )
            MqttManager.subscribe(topic)
        elif self.commands[page_cursor_key] == "mqtt publish":
            topic = HwMan.write_from_keyboard_to_oled(
                initial_text="topic: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
            message = HwMan.write_from_keyboard_to_oled(
                initial_text="message: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
            MqttManager.publish(topic, message)
