"""
This module contains the hardware manager class.
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=no-member
import os
from time import sleep_ms
from machine import I2C, Pin, SPI
from ssd1306 import SSD1306_I2C
import sd_card.sdcard
from pins_declarations import Pins
from rotary.rotary_irq_pico import RotaryIRQ

OLED_I2C = I2C(
    0,
    scl=Pin(Pins.OLED_SCL),
    sda=Pin(Pins.OLED_SDA),
    freq=200000
)
KEYBOARD_I2C = I2C(
    1,
    scl=Pin(Pins.KEYBOARD_SCL),
    sda=Pin(Pins.KEYBOARD_SDA)
)
SD_READER_SPI = SPI(
    1,
    baudrate=40000000,
    sck=Pin(Pins.SD_READER_SCK),
    mosi=Pin(Pins.SD_READER_MOSI),
    miso=Pin(Pins.SD_READER_MISO)
)
OLED_HEIGHT = 64
OLED_WIDTH = 128
ESC = chr(27)
NULL = '\x00'
BKSP = '\x08'
ENTER = '\r'


class HardwareManager:
    """
    This class is used to centralize the hardware managment.
    All the device connected hardware is instanciated here
    and can be accessed from any module only
    through this class.
    """
    def __init__(self):
        self.oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, OLED_I2C)
        self.keyboard = KEYBOARD_I2C.scan()[0]
        self.sd_reader = sd_card.sdcard.SDCard(
            SD_READER_SPI, Pin(Pins.SD_READER_CS)
        )
        self.encoder = RotaryIRQ(
            pin_num_clk=Pins.ENCODER_CLK,
            pin_num_dt=Pins.ENCODER_DT,
            min_val=0,
            max_val=24,
            reverse=False,
            pull_up=True,
            range_mode=RotaryIRQ.RANGE_WRAP,
        )
        self.select_button = Pin(Pins.SELECT_BUTTON, Pin.IN, Pin.PULL_UP)
        self.fast_button = Pin(Pins.FAST_BUTTON, Pin.IN, Pin.PULL_UP)
        self.leds_list = [
            Pin(Pins.LED_0, Pin.OUT),
            Pin(Pins.LED_1, Pin.OUT),
            Pin(Pins.LED_2, Pin.OUT),
            Pin(Pins.LED_3, Pin.OUT),
            Pin(Pins.LED_4, Pin.OUT),
            Pin(Pins.LED_5, Pin.OUT),
            Pin(Pins.LED_6, Pin.OUT),
            Pin(Pins.LED_7, Pin.OUT),
            Pin(Pins.LED_8, Pin.OUT),
            Pin(Pins.LED_9, Pin.OUT)
        ]

    def write_from_keyboard_to_oled(
        self,
        initial_text: str,
        exit_text: str,
        abort_tex: str
    ) -> str or None:
        """
        Write a string from the i2c keyboard connected to the device,
        the string is displayed on the oled while the user is
        typing, when the user presses the enter key the string is returned.
        - Args:
            - initial_text: the text to display before the user starts typing
            - exit_text: the text to display when the user presses
                the enter key
            - abort_text: the text to display when the user presses the ESC key
        - Returns:
            - the string typed by the user
            - None if the user presses the ESC key
        """
        char = str()
        i = int()
        word = str()
        self.show_msg(initial_text)
        while char != ESC:
            c_encoded = KEYBOARD_I2C.readfrom(self.keyboard, 1)
            char = c_encoded.decode()
            if char not in (NULL, ESC, BKSP, ENTER):
                print(c_encoded, char)
                word += char
                self.oled.text(char, i, 8)
                self.oled.show()
                i += 8
            elif char == BKSP:
                word = word[:-1]
                self.oled.fill_rect(i-8, 8, 8, 8, 0)
                self.oled.show()
                i -= 8
            elif char == ENTER:
                self.show_msg(exit_text)
                return word
            elif char == ESC:
                self.show_msg(abort_tex)
                return None
            sleep_ms(5)

    def show_msg(self, msg: str) -> None:
        """
        This method is used to display a message on the oled
        while the user is typing.
        """
        self.oled.fill(0)
        self.oled.text(msg, 0, 0)
        self.oled.show()

    def mount_card(self) -> None:
        """
        This method is used to mount the sd card.
        """
        try:
            vfs = os.VfsFat(self.sd_reader)
            os.mount(vfs, '/sd')
            return True
        except OSError:
            return False

    def unmount_card(self) -> None:
        """
        This method is used to unmount the sd card.
        """
        try:
            os.umount('/sd')
            return True
        except OSError:
            return False

    def list_sd_card_files(self) -> list:
        """
        This method is used to list the files on the sd card.
        - Returns:
            - the list of files on the sd card
        """
        return os.listdir("/sd")

    def format_card(self) -> None:
        """
        This method is used to format the sd card.
        """
        try:
            os.VfsFat.mkfs(self.sd_reader)
        except OSError:
            print("cannot format card")

    def set_led_bar(self, value) -> None:
        """
        Set the led bar to the given value
        - Args:
            - value: the value to set the led bar to
                it can be a number from 0 to 10
                where 0 is all the leds off
                and 10 is all the leds on
        """
        for i in range(10):
            if i < value:
                self.leds_list[i].value(1)
            else:
                self.leds_list[i].value(0)

    def startup_sequence(self) -> None:
        """
        This method is used to show the startup sequence.
        It is called when the device is powered on.
        """
        for i in range(11):
            self.set_led_bar(i)
            sleep_ms(100)
        self.set_led_bar(0)
        self.oled.fill(0)
        self.oled.text("mqtt_injector", 12, 12)
        self.oled.text("[", 0, 32)
        self.oled.text("]", 120, 32)
        self.oled.show()
        for i in range(14):
            self.oled.text("\u25AF", 8+i*8, 32)
            self.oled.show()
            sleep_ms(50)

    def hardware_check(self):
        """Check if all the hardware is connected and working"""
        raise NotImplementedError
