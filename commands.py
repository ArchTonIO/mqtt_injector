from wireless_tools import wlan_manager
from  hardware_manager import h_man
from time import sleep

class command_executer():
    def __init__(self):
        self.wlan=wlan_manager()
        self.commands={
            (1, 0): "wlan scan",
            (1, 1): "wlan status",
            (1, 2): "wlan connect",
            5: "wlan insert password"
        }

    def execute(self, pages_manager,
                page_cursor_key: tuple) -> None:
        try:
            print("executing command:",
                    self.commands[page_cursor_key])
        except:
            print("executing command:",
                    self.commands[page_cursor_key[0]])
        if page_cursor_key[0]!=5:
            if self.commands[page_cursor_key]=="wlan scan":
                h_man.oled.fill(0)
                h_man.oled.text("scanning...", 0, 0)
                h_man.oled.show()
                command_output=self.wlan.scan()
                self.wlan.saved_ssids=command_output["ssids"]
                entries=list()
                for i in range(len(command_output["ssids"])):
                    entries.append(command_output["ssids"][i][0:8]+" "
                                    +str(command_output["rssi"][i]))
                entries.append("back")
                pages_manager.add_page(page_id=5,
                                        leaf_attr=True,
                                        entries=entries)
                pages_manager.target_page=pages_manager.pages[-1]
                pages_manager.__display_page()
            elif self.commands[page_cursor_key]=="wlan status":
                h_man.oled.fill(0)
                connected=self.wlan.status()["isconnected"]
                conn_data=self.wlan.status()["ifconfig"]
                if connected:
                    h_man.oled.text("wlan connected", 0, 0)
                    h_man.oled.text("ip:"+conn_data[0], 0, 11)
                    h_man.oled.text("msk:"+conn_data[1], 0, 22)
                    h_man.oled.text("gate:"+conn_data[2], 0, 33)
                    h_man.oled.show()
                    timer=5
                    while timer>0:
                        h_man.oled.fill_rect(0, 44, 128, 8, 0)
                        h_man.oled.text("homepage in"+str(timer)+"...", 0, 44)
                        h_man.oled.show()
                        sleep(1)
                        timer-=1
                    pages_manager.target_page=pages_manager.pages[0]
                    pages_manager.__display_page()
                else:
                    h_man.oled.text("wlan not connected", 0, 0)
                    timer=5
                    while timer>0:
                        h_man.oled.fill_rect(0, 11, 128, 8, 0)
                        h_man.oled.text("homepage in"+str(timer)+"...", 0, 44)
                        h_man.oled.show()
                        sleep(1)
                        timer-=1

        elif self.commands[page_cursor_key[0]]=="wlan insert password":
            pages_manager.destroy_last_page()
            password=h_man.write_from_keyboard_to_oled()
            if password!=None:
                isconnected=self.wlan.connect(self.wlan.saved_ssids[page_cursor_key[1]], password)
                if isconnected:
                    h_man.oled.fill(0)
                    h_man.oled.text("connected!", 0, 0)
                    h_man.oled.show()
                    sleep(2)
                    pages_manager.target_page=pages_manager.pages[0]
                    pages_manager.__display_page()
                else:
                    h_man.oled.fill(0)
                    h_man.oled.text("failed!", 0, 0)
                    h_man.oled.show()
                    sleep(2)
                    pages_manager.target_page=pages_manager.pages[0]
                    pages_manager.__display_page()