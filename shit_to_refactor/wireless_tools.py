"""
This module contains the WlanManager class.
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
import network


class WlanManager():
    """
    This class is used to manage the wireless connection
    of the device.
    """
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.scan_called = bool()
        self.saved_ssids = []
        self.saved_passwords = []

    def scan(self) -> dict:
        """
        This method is used to scan the wireless networks.
        - Args:
            - None.
        - Returns:
            - A dictionary built as follows:
                - "ssids": a list of the ssid (name) of the found networks.
                - "rssi": a list of the rssi of the found networks.
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

    def connect(self, ssid: str, password: str) -> bool:
        """
        This method is used to connect to a wireless network.
        - Args:
            - ssid: the network ssid.
            - password: the password to connect to the network.
        - Returns:
            - True if the connection is successful, False otherwise.
        """
        self.wlan.connect(ssid, password)
        return self.wlan.isconnected()

    def disconnect(self) -> None:
        """
        This method is used to disconnect from the wireless network.
        - Args:
            - None.
        - Returns:
            - None.
        """
        self.wlan.disconnect()

    def status(self) -> dict:
        """
        This method is used to get the status of the wireless connection.
        - Args:
            - None.
        - Returns:
            - A dictionary built as follows:
                - "isconnected": True if the device is connected to a network,
                    False otherwise.
                - "ifconfig": a list containing the ip address, subnet mask,
                    gateway and dns server.
        """
        return {
            "isconnected": self.wlan.isconnected(),
            "ifconfig": self.wlan.ifconfig()
        }
