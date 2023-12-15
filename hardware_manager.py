""" Centralize the hardware managment. """
from time import sleep_ms

from machine import I2C, Pin, SPI
from ssd1306 import SSD1306_I2C

from pins_declarations import Pins
from rotary.rotary_irq_pico import RotaryIRQ
import sd_card.sdcard


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
CHAR_WIDTH = 8
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

    Attributes
    ----------
    oled : the oled display, it is a ssd1306 oled, 128x64 pixels.
    keyboard : the i2c keyboard.
    sd_reader : the sd card reader.
    encoder : the rotary encoder.
    select_button : the select button, it is a push button and its used
    to select an option.
    fast_button : the fast button, no one knows what it does.
    leds_list : the list of the 10 leds of the led bar.
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
    ) -> str | None:
        """
        Write a string from the i2c keyboard connected to the device,
        the string is displayed on the oled while the user is
        typing, when the user presses the enter key the string is returned.

        Parameters
        ----------
        initial_text : the text to display before the user starts typing
        exit_text : the text to display when the user presses the 'enter' key
        abort_text : the text to display when the user presses the ESC key

        Returns
        -------
        str : the string typed by the user
        None : if the user presses the ESC key
        """
        char = ""
        i = 0
        word = ""
        self.show_msg(initial_text)
        while char != ESC:
            c_encoded = KEYBOARD_I2C.readfrom(self.keyboard, 1)
            char = c_encoded.decode()
            if char not in (NULL, ESC, BKSP, ENTER):
                print(c_encoded, char)
                word += char
                self.oled.text(char, i, CHAR_WIDTH)
                self.oled.show()
                i += CHAR_WIDTH
            elif char == BKSP:
                word = word[:-1]
                self.oled.fill_rect(
                    i - CHAR_WIDTH,
                    CHAR_WIDTH,
                    CHAR_WIDTH,
                    CHAR_WIDTH,
                    0
                )
                self.oled.show()
                i -= CHAR_WIDTH
            elif char == ENTER:
                self.show_msg(exit_text)
                return word
            elif char == ESC:
                self.show_msg(abort_tex)
                return
            sleep_ms(5)
        return

    def show_msg(self, msg: str) -> None:
        """
        Display a message on the oled while the user is typing.

        Parameters
        ----------
        msg : the message to display
        """
        self.oled.fill(0)
        self.oled.text(msg, 0, 0)
        self.oled.show()

    def set_led_bar(self, value) -> None:
        """
        Set the led bar to the given value.
        Parameters
        ---------

        value : the value to set the led bar to it can be a number from 0 to 10
        where 0 is all the leds off and 10 is all the leds on
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
        self.set_led_bar(0)
        self.oled.fill(0)
        self.oled.text("[", 0, 32)
        self.oled.text("]", 120, 32)
        self.oled.show()
        arrow_body = ""
        arrow_head = ">"
        percentage = 0
        for i in range(14):
            if i < 10:
                self.set_led_bar(i)
            else:
                self.set_led_bar(10)
            arrow_head_position = 8 + i * 8
            self.oled.fill_rect(8, 32, 112, 8, 0)
            self.oled.text(arrow_body, 8, 32)
            self.oled.text(arrow_head, arrow_head_position, 32)
            self.oled.fill_rect(56, 48, 16, 8, 0)
            self.oled.text(f"{percentage}%", 56, 48)
            percentage += 7
            self.oled.show()
            sleep_ms(50)
            arrow_body = f"{arrow_body}="
        self.oled.fill(0)
        self.oled.text("mqtt_injector", 12, 12)
        self.oled.text("v0.1", 12, 24)
        self.oled.show()
        self.set_led_bar(0)
        sleep_ms(2000)
        self.oled.fill(0)
        self.oled.show()

    def hardware_check(self):
        """Check if all the hardware is connected and working"""
        raise NotImplementedError
