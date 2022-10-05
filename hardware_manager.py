from time import sleep_ms
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from rotary.rotary_irq_pico import RotaryIRQ

class h_man:
    OLED_WIDTH=128
    OLED_HEIGHT=64
    OLED_I2C=I2C(0, scl=Pin(9), sda=Pin(8), freq=200000)
    oled=SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, OLED_I2C)
    encoder=RotaryIRQ(pin_num_clk=12,
                        pin_num_dt=13,
                        min_val=0,
                        max_val=24,
                        reverse=True,
                        range_mode=RotaryIRQ.RANGE_WRAP,
                        pull_up=True)
    select_button=Pin(16, Pin.IN, Pin.PULL_UP)
    @staticmethod
    def write_from_keyboard_to_oled(initial_text="password:",
                                    exit_text="entering...",
                                    abort_tex="aborting...") -> str:
        KEYBOARD_I2C=I2C(1, scl=Pin(7), sda=Pin(6))
        keyboard=KEYBOARD_I2C.scan()[0]
        ESC=chr(27)
        NUL='\x00'
        BCKSP='\x08'
        ENTER='\r'
        c=str()
        i=int()
        word=str()
        h_man.oled.fill(0)
        h_man.oled.text(initial_text, 0, 0)
        h_man.oled.show()
        while (c!=ESC):
            c_encoded=KEYBOARD_I2C.readfrom(keyboard, 1)
            c=c_encoded.decode()
            if (c!=NUL and c!=ESC
            and c!=BCKSP and c!=ENTER):
                print(c_encoded, c)
                word+=c
                h_man.oled.text(c, i, 8)
                h_man.oled.show()
                i+=8
            elif c==BCKSP:
                word=word[:-1]
                h_man.oled.fill_rect(i-8, 8, 8, 8, 0)
                h_man.oled.show()
                i-=8
            elif c==ENTER:
                h_man.oled.fill(0)
                h_man.oled.text(exit_text, 0, 0)
                h_man.oled.show()
                return word
            elif c==ESC:
                h_man.oled.fill(0)
                h_man.oled.text(abort_tex, 0, 0)
                h_man.oled.show()
                return None
            sleep_ms(5)