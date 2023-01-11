"""
This module contains the hardware manager class.
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
from time import sleep_ms

from machine import I2C, Pin
from ssd1306 import SSD1306_I2C

from rotary.rotary_irq_pico import RotaryIRQ


class HwMan:
    """
    This class is used to centralize the hardware managment.
    All the device connected hardware is instanciated here
    and can be accessed from any module only
    through this class.
    """
    OLED_HEIGHT = 64
    OLED_WIDTH = 128
    OLED_I2C = I2C(0, scl=Pin(9), sda=Pin(8), freq=200000)
    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, OLED_I2C)
    encoder = RotaryIRQ(
        pin_num_clk=12,
        pin_num_dt=13,
        min_val=0,
        max_val=24,
        reverse=False,
        range_mode=RotaryIRQ.RANGE_WRAP,
        pull_up=True
    )
    select_button = Pin(14, Pin.IN, Pin.PULL_UP)
    fast_button = Pin(16, Pin.IN, Pin.PULL_UP)
    leds_list = [
        Pin(28, Pin.OUT),
        Pin(27, Pin.OUT),
        Pin(26, Pin.OUT),
        Pin(22, Pin.OUT),
        Pin(21, Pin.OUT),
        Pin(20, Pin.OUT),
        Pin(19, Pin.OUT),
        Pin(18, Pin.OUT),
        Pin(17, Pin.OUT),
        Pin(15, Pin.OUT)
    ]

    @staticmethod
    def write_from_keyboard_to_oled(
        initial_text="password:",
        exit_text="entering...",
        abort_tex="aborting..."
    ) -> str or None:
        """
        This method is used to write a string from the i2c keyboard connected
        to the device, the string is displayed on the oled while the user is
        typing, when the user presses the enter key the string is returned.
        - Args:
            - initial_text: the text to display before the user starts typing
            - exit_text: the text to display when the user presses
                the enter key
            - abort_text: the text to display when the user presses the esc key
        - Returns:
            - the string typed by the user
            - None if the user presses the esc key
        """
        keyboard_i2c = I2C(1, scl=Pin(7), sda=Pin(6))
        keyboard = keyboard_i2c.scan()[0]
        esc = chr(27)
        null = '\x00'
        bksp = '\x08'
        enter = '\r'
        char = str()
        i = int()
        word = str()
        HwMan.oled.fill(0)
        HwMan.oled.text(initial_text, 0, 0)
        HwMan.oled.show()
        while char != esc:
            c_encoded = keyboard_i2c.readfrom(keyboard, 1)
            char = c_encoded.decode()
            if char not in (null, esc, bksp, enter):
                print(c_encoded, char)
                word += char
                HwMan.oled.text(char, i, 8)
                HwMan.oled.show()
                i += 8
            elif char == bksp:
                word = word[:-1]
                HwMan.oled.fill_rect(i-8, 8, 8, 8, 0)
                HwMan.oled.show()
                i -= 8
            elif char == enter:
                HwMan.oled.fill(0)
                HwMan.oled.text(exit_text, 0, 0)
                HwMan.oled.show()
                return word
            elif char == esc:
                HwMan.oled.fill(0)
                HwMan.oled.text(abort_tex, 0, 0)
                HwMan.oled.show()
                return None
            sleep_ms(5)

    @staticmethod
    def set_led_bar(value) -> None:
        """
        Set the led bar to the given value
        - Args:
            - value: the value to set the led bar to
                it can be a number from 0 to 10
                where 0 is all the leds off
                and 10 is all the leds on
        - Returns:
            - None
        """
        for i in range(10):
            if i < value:
                HwMan.leds_list[i].value(1)
            else:
                HwMan.leds_list[i].value(0)

    @staticmethod
    def startup_sequence() -> None:
        """
        This method is used to show the startup sequence.
        It is called when the device is powered on.
        - Args:
            - None
        - Returns:
            - None
        """
        for i in range(11):
            HwMan.set_led_bar(i)
            sleep_ms(100)
        HwMan.set_led_bar(0)
        HwMan.oled.fill(0)
        HwMan.oled.text("mqtt_injector", 12, 12)
        HwMan.oled.text("[", 0, 32)
        HwMan.oled.text("]", 120, 32)
        HwMan.oled.show()
        for i in range(14):
            HwMan.oled.text("#", 8+i*8, 32)
            HwMan.oled.show()
            sleep_ms(50)

    @staticmethod
    def hardware_check():
        """Check if all the hardware is connected and working"""
        return
