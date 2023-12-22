""" Manage the commands of the device. """
import gc
import json
import os
from random import randint

import network
import uos
from umqtt.simple import MQTTClient

from hardware_manager import HardwareManager


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
        entries, parent = func(*args, **kwargs)
        return (
            {
                "page_uid": str(randint(10, 99)),
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
    def __init__(self, hardware_manager: HardwareManager) -> None:
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.scan_called = False
        self.saved_ssids = []
        self.saved_passwords = []
        self.hardware_manager = hardware_manager

    @create_response_page
    def scan_networks(self) -> tuple:
        """
        Scan the wireless networks.

        Returns
        -------
        dict : a dictionary compliant with the pages_manager module to
        build the page.
        The parent here is hardcoded to "B0" because this is the
        uid of the wlan page in the pages_manager module.
        """
        data = self._scan()
        ssid = data["ssids"]
        rssi = data["rssi"]
        return (
            [
                f"{ssid[:8]} {rssi}" for ssid, rssi in zip(ssid, rssi)
            ],
            "B0"
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
    def connect(self, ssid: str, password: str) -> tuple:
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
        self.wlan.connect(ssid, password)
        return (
            [str(self.wlan.isconnected())],
            "B0"
        )

    @create_response_page
    def disconnect(self) -> tuple:
        """ Disconnect from the wireless network. """
        self.wlan.disconnect()
        return (
            [str(self.wlan.isconnected())],
            "B0"
        )

    def status(self) -> dict:
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
        return {
            "isconnected": self.wlan.isconnected(),
            "ifconfig": self.wlan.ifconfig()
        }


class BleManager:
    """ Manage the device bluetooth connection. """
    def __init__(self) -> None:
        # self.ble = None
        # self.ble.active(True)
        # self.scan_called = bool()
        # self.saved_addresses = []
        raise NotImplementedError

    def scan(self) -> dict:
        """ Scan for bluetooth devices. """
        raise NotImplementedError

    def connect(self, address: str) -> bool:
        """ Connect to a bluetooth device. """
        raise NotImplementedError

    def disconnect(self) -> None:
        """ Disconnect from a bluetooth device. """
        raise NotImplementedError

    def status(self) -> dict:
        """ Get the status of the bluetooth connection. """
        raise NotImplementedError


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
    def __init__(self) -> None:
        self.mqtt_client: MQTTClient
        self.client_name = ""
        self.broker_ip = ""
        self.keepalive = 0
        self.fast_reading_topics = []
        self.fast_publish_topic_msg = {}

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
            ["connection created"],
            "D0"
        )


    @create_response_page
    def connect(self) -> tuple:
        """
        Connect to the broker.
        """
        self.mqtt_client.connect()
        return (
            [str(self.mqtt_client.isconnected())],
            "D0"
        )

    @create_response_page
    def status(self) -> tuple:
        """
        Return the status of the connection.
        """
        return(
            [str(self.mqtt_client.isconnected())],
            "D0"
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
            [f"subscribed to {topic}"],
            "D0"
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
            [f"published to {topic}"],
            "D0"
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
            [f"published to {self.fast_publish_topic_msg[key][0]}"],
            "D0"
        )


class SdManager:
    """ Manage the sd card. """
    def __init__(self, h_man: HardwareManager) -> None:
        self.sd_reader = h_man.sd_reader

    def mount_card(self) -> None:
        """ Mount the sd card. """
        try:
            vfs = os.VfsFat(self.sd_reader)
            os.mount(vfs, '/sd')
            return True
        except OSError:
            return False

    def unmount_card(self) -> None:
        """ Unmount the sd card. """
        try:
            os.umount('/sd')
            return True
        except OSError:
            return False

    def list_sd_card_files(self) -> list:
        """
        List the files on the sd card.

        Returns
        -------
        list : the list of files on the sd card
        """
        return os.listdir("/sd")

    def format_card(self) -> None:
        """ Format the sd card. """
        try:
            os.VfsFat.mkfs(self.sd_reader)
        except OSError:
            print("cannot format card")

    def read_log_file(self) -> str:
        """
        Read the log file.

        Returns
        -------
        str : the content of the log file.
        """
        with open("/sd/log.txt", "r", encoding="utf-8") as log_file:
            return log_file.read()

    def excecute_file(self, file: str) -> None:
        """
        Excecute a python file.

        Parameters
        ----------
        file : the path of the file to excecute.
        """
        try:
            exec(open(file, encoding="utf-8").read())
        except OSError:
            print("cannot excecute file")


class ConfigManager:
    """
    Manage the device configuration.

    Attributes
    ----------
    config : the configuration dictionary.
    """
    def __init__(self) -> None:
        self.config = {
            "boot hardware_check": True,
            "boot animation": True,
            "error recovery": True,
            "led brightness": 3,
            "oled brightness": 3,
            "oled contrast": 3,
            "encoder_reverse": False,
        }

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

    @create_response_page
    def get_available_sram(self) -> tuple:
        """
        Get the available sram.

        Returns
        -------
        int : the available sram.
        """
        return(
            [f"{int(gc.mem_alloc()/1024)} KB/264 KB"],
            "F0",
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
            [f"{int(free_flash/1024)} KB/{int(total_flash/1024)} KB"],
            "F0",
        )
