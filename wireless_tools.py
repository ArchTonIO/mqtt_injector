import network

class wlan_manager():
    def __init__(self):
        self.wlan=network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.scan_called=bool()
        self.saved_ssids=list()
        self.saved_passwords=list()

    def scan(self) -> dict:
        self.scan_called=True
        output=self.wlan.scan()
        ssids_list=list()
        channels_list=list()
        rssi_list=list()
        security_list=list()
        for entry in output:
            ssids_list.append(entry[0].decode("utf-8"))
            channels_list.append(entry[2])
            rssi_list.append(entry[3])
            security_list.append(entry[4])
        return{
            "ssids": ssids_list,
            "rssi": rssi_list,
        }

    def connect(self, ssid: str, password: str) -> bool:
        self.wlan.connect(ssid, password)
        return self.wlan.isconnected()

    def disconnect(self) -> None:
        self.wlan.disconnect()

    def status(self) -> dict:
        return {
            "isconnected": self.wlan.isconnected(),
            "ifconfig": self.wlan.ifconfig()
        }