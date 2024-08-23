""" Manage the commands of the device. """
import _thread
import gc
import json
import os
import random
from time import sleep_ms
import socket
from device_logging import Logger
import uping

import network
import uos
from umqtt.simple import MQTTClient

from hardware_manager import HardwareManager

core_1_flag = True

def _enable_available_sram_led_indicator(hw_man) -> None:
    global core_1_flag
    while core_1_flag:
        available_sram = int(gc.mem_alloc() / 1024)
        turned_on_leds = int((available_sram * 10) / 264)
        hw_man.set_led_bar(turned_on_leds)
        sleep_ms(100)

def generate_page_uid(length: int = 16) -> str:
    """ Generate a random page uid. """
    characters = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )
    return''.join(random.choice(characters) for _ in range(length))


def normalize_entries_len(entries: list[str]) -> list[str]:
    """ Normalize the length of the entries to fit the oled screen. """
    new_entries = []
    for entry in entries:
        if len(entry) <= 14:
            new_entries.append(entry)
            continue
        entry = [entry[i:i+14] for i in range(0, len(entry), 14)]
        new_entries.extend(entry)
    return new_entries


def create_response_page(func):
    """
    Decorator to create the response page.

    Parameters
    ----------
    func : the function to decorate.

    Returns
    -------
    func : the decorated function.
    """
    def wrapper(*args, **kwargs):
        """
        Create the response page.

        Returns
        -------
        dict : a dictionary compliant with the pages_manager module to
        build the page.
        """
        name, entries, parent = func(*args, **kwargs)
        entries.append("back")
        return (
            {
                "name": name,
                "page_uid": generate_page_uid(),
                "entries": entries,
                "parent": parent,
                "childs": {},
                "cursor": ">",
                "right_cursor": "<",
                "cursor_default_position": 0
            }
        )
    return wrapper


class WlanManager:
    """
    Manage the wireless connection of the device.

    Attributes
    ----------
    wlan : the wireless connection instance.
    scan_called : a boolean indicating if the scan method has been called.
    saved_ssids : a list of the saved ssids.
    saved_passwords : a list of the saved passwords.
    hardware_manager : an instance of the HardwareManager class.
    """
    def __init__(
        self,
        hardware_manager: HardwareManager,
        add_command_calback
    ) -> None:
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.scan_called = False
        self.actual_ssid = ""
        self.actual_password = ""
        self.hardware_manager = hardware_manager
        self.add_command_calback = add_command_calback
        self.visible_networks = []
        self.logger = Logger("WLAN_MANAGER")
        self.wlan_page_uid = "ebu9n0VQjmh1bn3v"
        self._connect_to_known_networks()

    def _connect_to_known_networks(self) -> None:
        """
        Connect to the known networks.
        """
        data = self._scan()
        self.visible_networks = data["ssids"]
        self.logger.debug(f"visible networks: {self.visible_networks}")
        try:
            with open(
                "/sd/networks.json", "r", encoding="utf-8"
            ) as networks_file:
                networks = json.load(networks_file)
                for ssid, password in networks.items():
                    if ssid in self.visible_networks:
                        self.logger.debug(
                            f"connecting to {ssid} using password {password}"
                        )
                        self.connect(ssid, password, save=False)
                        break
        except OSError:
            self.logger.error("no networks file found !")


    @create_response_page
    def scan_networks(self) -> tuple:
        """
        Scan the wireless networks.

        Returns
        -------
        dict : a dictionary compliant with the pages_manager module to
        build the page.
        The parent here is hardcoded to "ebu9n0VQjmh1bn3v" because this is the
        uid of the wlan page in the pages_manager module.
        """
        data = self._scan()
        ssid = data["ssids"]
        rssi = data["rssi"]
        self.visible_networks = ssid
        entries = [f"{ssid[:8]} {rssi}" for ssid, rssi in zip(ssid, rssi)]
        [
            self.add_command_calback(entry, self.connect, [ssid, ])
            for entry, ssid in zip(entries, ssid)
        ]
        self.logger.info(f"networks scanned, found nertworks: {ssid}")
        return (
            "wlan scan command response",
            [
                f"{ssid[:8]} {rssi}" for ssid, rssi in zip(ssid, rssi)
            ],
            self.wlan_page_uid,
        )

    def _scan(self) -> dict:
        """
        Scan the wireless networks.

        Returns
        -------
        dict : a dictionary built as follows:
            "ssids" : a list of the ssid (name) of the found networks.
            "rssi" : a list of the rssi of the found networks.
            rssi is the signal strength of the network,
            the higher the value, the stronger the signal,
            please note that the value has a negative sign.
        """
        self.scan_called = True
        output = self.wlan.scan()
        ssids_list = []
        channels_list = []
        rssi_list = []
        security_list = []
        for entry in output:
            ssids_list.append(entry[0].decode("utf-8"))
            channels_list.append(entry[2])
            rssi_list.append(entry[3])
            security_list.append(entry[4])
        return {
            "ssids": ssids_list,
            "rssi": rssi_list,
        }

    @create_response_page
    def connect(
        self,
        ssid: str,
        password: str | None = None,
        save: bool = True
    ) -> tuple:
        """
        Connect to a wireless network.

        Parameters
        ----------
        ssid : the network ssid.
        password : the password to connect to the network.

        Returns
        -------
        bool : True if the connection is successful, False otherwise.
        """
        if not password:
            password = self.hardware_manager.write_from_keyboard_to_oled(
                "password:",
                "ok !",
                "aborting !"
            )
        if not password:
            return (
                "wlan connect command response",
                ["aborted !"],
                self.wlan_page_uid
            )
        self.logger.info(
            f"connecting to network {ssid} using password {password}"
        )
        self.wlan.connect(ssid, password)
        self.actual_ssid = ssid
        self.actual_password = password
        self._save_network() if save else None
        return (
            "wlan connect command response",
            [str(self.wlan.isconnected())],
            self.wlan_page_uid
        )

    @create_response_page
    def disconnect(self) -> tuple:
        """ Disconnect from the wireless network. """
        self.wlan.disconnect()
        return (
            "wlan disconnect command response",
            [str(self.wlan.isconnected())],
            self.wlan_page_uid
        )

    @create_response_page
    def status(self) -> tuple:
        """
        Get the status of the wireless connection.

        Returns
        -------
        dict : a dictionary built as follows:
            "isconnected" : True if the device is connected to a network,
            False otherwise.
            "ifconfig" : a list containing:
                0 : ip address
                1 : subnet mask
                2 : gateway
                3 : dns server
        """
        ifconfig = self.wlan.ifconfig()
        return (
                "wlan status command response",
                [
                    f"isconn: {self.wlan.isconnected()}",
                    "ip:",
                    ifconfig[0],
                    "subnet mask:",
                    ifconfig[1],
                    "gateway:",
                    ifconfig[2],
                ],
                self.wlan_page_uid
        )
    
    def _save_network(self) -> None:
        """
        Save a network to the device sd.
        """
        with open("/sd/networks.json", "a", encoding="utf-8") as networks_file:
            json.dump({self.actual_ssid: self.actual_password}, networks_file)
        self.logger.info(f"network connection {self.actual_ssid} saved !")

    def _scan_network(self, base_ip: str) -> list:
        """
        Scan the network for connected devices.

        Parameters
        ----------
        base_ip : the base ip address of the network.

        Returns
        -------
        list : a list of the connected devices.
        """
        connected_devices = []
        self.hardware_manager.oled.fill(0)
        self.hardware_manager.oled.text("scanning:", 0, 0)
        rect_start = len(base_ip) + 1
        for i in range(1, 255):
            percent = int((i / 255) * 100)
            self.hardware_manager.oled.fill_rect(
                rect_start * 8, 16, (len(str(i)) + 2) * 8, 16, 0
            )
            self.hardware_manager.oled.fill_rect(
                9 * 8, 0, (len(str(i)) + 2) * 8, 8, 0
            )
            self.hardware_manager.oled.text(f"{base_ip}.{i}", 0, 16)
            self.hardware_manager.oled.text(f"{percent}%", 10 * 8, 0)
            self.hardware_manager.show_progressbar(percent, 4)
            self.hardware_manager.oled.show()
            ip = f"{base_ip}.{i}"
            try:
                if uping.ping(ip):
                    connected_devices.append(ip)
            except OSError:
                pass
        self.hardware_manager.set_led_bar(0)
        return connected_devices

    @create_response_page
    def list_devices(self) -> tuple:
        """
        List the devices connected to the network.

        Returns
        -------
        dict : a dictionary compliant with the pages_manager module to
        build the page.
        The parent here is hardcoded to self.wlan_page_uid because this is the
        uid of the wlan page in the pages_manager module.
        """
        parts = self.wlan.ifconfig()[0].split(".")
        base_ip = '.'.join(parts[:-1])
        devices = self._scan_network(base_ip)
        devices.insert(0, "found devices:")
        return (
            "connected devices",
            devices,
            self.wlan_page_uid
        )


class BleManager:
    """ Manage the device bluetooth connection. """
    def __init__(self, add_command_calback) -> None:
        ...

    def scan(self) -> dict:
        """ Scan for bluetooth devices. """
        ...

    def connect(self, address: str) -> bool:
        """ Connect to a bluetooth device. """
        ...

    def disconnect(self) -> None:
        """ Disconnect from a bluetooth device. """
        ...

    def status(self) -> dict:
        """ Get the status of the bluetooth connection. """
        ...


class MqttManager:
    """
    Manage the device mqtt connection.

    Attributes
    ----------
    mqtt_client : the mqtt client instance.
    client_name : the mqtt client name.
    broker_ip : the mqtt broker ip address.
    keepalive : the mqtt keepalive.
    fast_reading_topics : a list of the topics to read.
    fast_publish_topic_msg : a dictionary containing the topics
    and the messages to publish.
    """
    def __init__(self, add_command_calback) -> None:
        self.mqtt_client: MQTTClient
        self.client_name = ""
        self.broker_ip = ""
        self.keepalive = 0
        self.fast_reading_topics = []
        self.fast_publish_topic_msg = {}
        self.add_command_calback = add_command_calback

    @staticmethod
    def subscribe_callback(topic: str, msg: str) -> None:
        """
        This is the callback function for the mqtt client.
        """
        print(topic, msg)

    @create_response_page
    def create_connection(self) -> tuple:
        """
        Create the connection with the parameters specified at init time.
        """
        self.mqtt_client = MQTTClient(
            self.client_name,
            self.broker_ip,
            keepalive=self.keepalive
        )
        self.mqtt_client.set_callback(
            self.subscribe_callback
        )
        return (
            "mqtt create connection response",
            ["connection created"],
            "Y9OQNRBTclzzFGtU"
        )


    @create_response_page
    def connect(self) -> tuple:
        """
        Connect to the broker.
        """
        self.mqtt_client.connect()
        return (
            "mqtt connect response",
            [str(self.mqtt_client.isconnected())],
            "Y9OQNRBTclzzFGtU"
        )

    @create_response_page
    def status(self) -> tuple:
        """
        Return the status of the connection.
        """
        return(
            "mqtt status response",
            [str(self.mqtt_client.isconnected())],
            "Y9OQNRBTclzzFGtU"
        )

    @create_response_page
    def subscribe(self, topic: str) -> tuple:
        """
        Subscribe to a topic.

        Parameters
        ---------
        topic : the topic to subscribe to.
        """
        self.mqtt_client.subscribe(topic)
        return (
            "mqtt subscribe response"
            [f"subscribed to {topic}"],
            "Y9OQNRBTclzzFGtU"
        )

    @create_response_page
    def publish(self, topic: str, msg: str) -> tuple:
        """
        Publish a message to a topic.

        Parameters
        ---------
        topic : the topic to publish to.
        msg : the message to publish.
        """
        self.mqtt_client.publish(topic, msg)
        return (
            "mqtt publish response",
            [f"published to {topic}"],
            "Y9OQNRBTclzzFGtU"
        )

    def check_messages_on_broker(self) -> None:
        """
        Check for messages on the broker.

        Returns
        -------
        dict : a dictionary containing the topics and the messages.
        """
        self.mqtt_client.check_msg()

    @create_response_page
    def fast_publish(self, key: str) -> tuple:
        """
        Publish a message to a topic.

        Parameters
        ---------
        key: the key of the topic and message to publish.
        """
        self.publish(
            self.fast_publish_topic_msg[key][0],
            self.fast_publish_topic_msg[key][1]
        )
        return (
            "mqtt fast publish response",
            [f"published to {self.fast_publish_topic_msg[key][0]}"],
            "Y9OQNRBTclzzFGtU"
        )


class SdManager:
    """ Manage the sd card. """
    def __init__(
        self,
        hw_man: HardwareManager,
        add_command_calback
    ) -> None:
        self.hw_man = hw_man
        self.parent_uid = "3piowGrCWbJkB9Jo"
        self.sd_reader = None
        self.add_command_calback = add_command_calback
        self.logger = Logger("SD_MANAGER")
        self.mount_card()

    @create_response_page
    def mount_card(self) -> None:
        """ Mount the sd card. """
        try:
            self.hw_man.initialize_sd_reader()
            self.sd_reader = self.hw_man.sd_reader
            vfs = os.VfsFat(self.sd_reader)
            os.mount(vfs, '/sd')
            self.logger.info("card mounted !")
            return (
                "mount card response",
                ["card mounted !"],
                self.parent_uid
            )
        except OSError:
            self.logger.error("card error !")
            return (
                "mount card response",
                ["card error !", "sd inserted ?"],
                self.parent_uid
            )

    @create_response_page
    def unmount_card(self) -> None:
        """ Unmount the sd card. """
        try:
            os.umount('/sd')
            return (
                "unmount card response",
                ["card umounted !"],
                self.parent_uid
            )
        except OSError:
            return ["card error !"], self.parent_uid

    @create_response_page
    def list_card_files(self) -> list:
        """
        List the files on the sd card.

        Returns
        -------
        list : the list of files on the sd card
        """
        try:
            files = os.listdir("/sd")
            res = [f"found {len(files)} files:", ""]
            res.extend(files)
            return "list sd card files response", res, self.parent_uid
        except OSError:
            return (
                "list card files response",
                ["list error !", "card mounted ?"], 
                self.parent_uid
            )

    @create_response_page
    def format_card(self) -> None:
        """ Format the sd card. """
        try:
            os.VfsFat.mkfs(self.sd_reader)
            return (
                "format card response",
                ["card formatted !"],
                self.parent_uid
            )
        except OSError:
            return "format card response", ["format error !"], self.parent_uid

    @create_response_page
    def read_log_file(self) -> str:
        """
        Read the log file.

        Returns
        -------
        str : the content of the log file.
        """
        with open("/logs/device.log", "r", encoding="utf-8") as log_file:
            return (
                "read log file response",
                normalize_entries_len(log_file.read().split("\n")),
                self.parent_uid
            )


    @create_response_page
    def excecute_file(self, file: str) -> None:
        """
        Excecute a python file.

        Parameters
        ----------
        file : the path of the file to excecute.
        """
        try:
            exec(open(file, encoding="utf-8").read())
            return (
                "excectue file response",
                ["excecution ok !"],
                self.parent_uid
            )
        except OSError:
            return (
                "excectue file response",
                ["excecution err !"],
                self.parent_uid
            )


class ConfigManager:
    """
    Manage the device configuration.

    Attributes
    ----------
    config : the configuration dictionary.
    """
    def __init__(
        self, hw_man: HardwareManager,
        add_command_calback
    ) -> None:
        self.hw_man = hw_man
        self.core_1_flag = True
        self.config = {
            "boot hardware_check": True,
            "boot animation": True,
            "error recovery": True,
            "led brightness": 3,
            "oled brightness": 3,
            "oled contrast": 3,
            "encoder_reverse": False,
        }
        self.add_command_calback = add_command_calback

    def load_config(self) -> dict:
        """
        Load the configuration from the config.json file.

        Returns
        -------
        dict : the configuration dictionary.
        """
        with open("config.json", "r", encoding="utf-8") as config_file:
            self.config = json.load(config_file)
        return self.config

    def set_boot_hardware_check(self, value: bool) -> None:
        """
        Set the boot hardware check configuration.

        Parameters
        ----------
        value : the value to set.
        """
        self.config["boot hardware_check"] = value

    def set_boot_animation(self, value: bool) -> None:
        """
        Set the boot animation configuration.

        Parameters
        ----------
        value : the value to set.
        """
        self.config["boot animation"] = value

    def set_error_recovery(self, value: bool) -> None:
        """
        Set the error recovery configuration.

        Parameters
        ----------
        value : the value to set.
        """
        self.config["error recovery"] = value

    def set_led_brightness(self, value: int) -> None:
        """
        Set the led brightness configuration.

        Parameters
        ----------
        value : the value to set.
        """
        self.config["led brightness"] = value

    def set_oled_brightness(self, value: int) -> None:
        """
        Set the oled brightness configuration.

        Parameters
        ----------
        value : the value to set.
        """
        self.config["oled brightness"] = value

    def set_oled_contrast(self, value: int) -> None:
        """
        Set the oled contrast configuration.

        Parameters
        ----------
        value : the value to set.
        """
        self.config["oled contrast"] = value

    def set_encoder_reverse(self, value: bool) -> None:
        """
        Set the encoder reverse configuration.

        Parameters
        ----------
        value : the value to set.
        """
        self.config["encoder_reverse"] = value

    def save_config(self) -> None:
        """
        Save the configuration to the config.json file.
        """
        with open("config.json", "w", encoding="utf-8") as config_file:
            json.dump(self.config, config_file)

    def enable_available_sram_led_indicator(self) -> None:
        """
        Enable the available sram led indicator.
        """
        sleep_ms(200)
        _thread.start_new_thread(_enable_available_sram_led_indicator, (self.hw_man, ))

    def disable_available_sram_led_indicator(self) -> None:
        """
        Disable the available sram led indicator.
        """
        global core_1_flag
        core_1_flag = False
        self.hw_man.set_led_bar(0)

    @create_response_page
    def get_available_sram(self) -> tuple:
        """
        Get the available sram.

        Returns
        -------
        int : the available sram.
        """
        return(
            "get available sram response",
            [f"{int(gc.mem_alloc()/1024)} KB/264 KB"],
            "gv5qU62isrkomZHr",
        )

    @create_response_page
    def get_available_flash(self) -> tuple:
        """
        Get the available flash memory.

        Returns
        -------
        the available flash memory.
        """
        fs_stats = uos.statvfs("/")
        total_flash = fs_stats[0] * fs_stats[2]
        free_flash = fs_stats[0] * fs_stats[3]
        return(
            "get available flash response",
            [f"{int(free_flash/1024)} KB/{int(total_flash/1024)} KB"],
            "gv5qU62isrkomZHr",
        )
