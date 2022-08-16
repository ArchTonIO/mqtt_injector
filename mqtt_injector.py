from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from rotary_irq_pico import RotaryIRQ
from pages_manager import pages_manager

class mqtt_injector():
    def __init__(self):
        OLED_WIDTH=128
        OLED_HEIGHT=64
        OLED_I2C=I2C(0, scl=Pin(9), sda=Pin(8), freq=200000)
        self.oled=SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, OLED_I2C)
        self.encoder=RotaryIRQ(pin_num_clk=12,
                                pin_num_dt=13,
                                min_val=0,
                                max_val=24,
                                reverse=True,
                                range_mode=RotaryIRQ.RANGE_WRAP,
                                pull_up=True)
        self.select_button=machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pages_manager=pages_manager(self.oled, 
                                        self.encoder,
                                        self.select_button)
        self.pages_manager.add_page(page_id=0, entries=["wireless_tools",
                                                        "mqtt_tools",
                                                        "sensors",
                                                        "config",
                                                        "save config",
                                                        "hardware_check",
                                                        "back"])
        self.pages_manager.add_page(page_id=1, entries=["w_shit0",
                                                        "w_shit1",
                                                        "w_shit2",
                                                        "w_shit3",
                                                        "w_shit4",
                                                        "back"])
        self.pages_manager.add_page(page_id=2, entries=["m_shit0",
                                                        "m_shit1",
                                                        "m_shit2",
                                                        "m_shit3",
                                                        "m_shit4",
                                                        "back"])
        self.pages_manager.add_page(page_id=3, entries=["s_shit0",
                                                        "s_shit1",
                                                        "s_shit2",
                                                        "s_shit3",
                                                        "s_shit4",
                                                        "back"])
        self.pages_manager.add_page(page_id=4, entries=["c_shit0",
                                                        "c_shit1",
                                                        "c_shit2",
                                                        "c_shit3",
                                                        "c_shit4",
                                                        "back"])
        self.pages_manager.add_page(page_id=5, entries=["h_c_shit0",
                                                        "h_c_shit1",
                                                        "h_c_shit2",
                                                        "h_c_shit3",
                                                        "h_c_shit4",
                                                        "back"])
        self.pages_manager.loop()

device=mqtt_injector()