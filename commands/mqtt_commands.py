
"""
This file contains the commands related to the mqtt client.
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
from time import sleep
from mqtt.mqtt_manager import MqttManager
from commands.commands_dispatcher import CommandsDispatcher
from hardware_manager import HwMan

class MqttComnands(CommandsDispatcher):
    """
    This class is used to manage the mqtt commands.
    """
    def __init__(self):
        self.commands = super.commands
        self.pages_manager = super.pages_manager
        self.hw_man = HwMan
        self.mqtt_man = MqttManager

    def exec(
        self,
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
            self.mqtt_man.fast_publish("sas")
        elif self.commands[page_cursor_key] == "mqtt set_conn":
            self.__set_connection()
        elif self.commands[page_cursor_key] == "fast connect":
            self.__fast_connect()
        elif self.commands[page_cursor_key] == "mqtt connect":
            self.__conn_and_get_status(conn=True)
        elif self.commands[page_cursor_key] == "mqtt status":
            self.__conn_and_get_status(conn=False)
        elif self.commands[page_cursor_key] == "mqtt subscribe":
            self.__subscribe()
        elif self.commands[page_cursor_key] == "mqtt publish":
            self.__publish()

    def __set_connection(self):
        self.mqtt_man.broker_ip = HwMan.write_from_keyboard_to_oled(
                initial_text="mqtt broker ip: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
        self.mqtt_man.client_name = HwMan.write_from_keyboard_to_oled(
            initial_text="mqtt client name: ",
            exit_text="got it!",
            abort_tex="exiting..."
        )
        self.mqtt_man.keepalive = int(
            HwMan.write_from_keyboard_to_oled(
                initial_text="mqtt keepalive: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
        )
        self.mqtt_man.create_connection()

    def __fast_connect(self):
        self.mqtt_man.broker_ip = HwMan.write_from_keyboard_to_oled(
            initial_text="mqtt broker ip: ",
            exit_text="got it!",
            abort_tex="exiting..."
        )
        self.mqtt_man.broker_ip = "192.168.1.17"
        self.mqtt_man.client_name = "mqtt_injector"
        self.mqtt_man.keepalive = 60
        self.mqtt_man.create_connection()
        self.mqtt_man.connect()

    def __conn_and_get_status(self, conn: bool):
        if conn:
            self.mqtt_man.connect()
        HwMan.oled.fill(0)
        if self.mqtt_man.status():
            HwMan.oled.text("connected!", 0, 0)
        else:
            HwMan.oled.text("no connection!", 0, 0)
        self.hw_man.oled.show()
        sleep(2)
        self.pages_manager.target_page = self.pages_manager.pages[3]
        self.pages_manager.__display_page()

    def __subscribe(self):
        topic = HwMan.write_from_keyboard_to_oled(
            initial_text="topic: ",
            exit_text="subscribed to {topic}",
            abort_tex="exiting..."
        )
        self.mqtt_man.subscribe(topic)

    def __publish(self):
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
        self.mqtt_man.publish(topic, message)