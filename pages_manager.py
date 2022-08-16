from page import page
from time import sleep
from machine import Pin
from ssd1306 import SSD1306_I2C
from rotary_irq_pico import RotaryIRQ

class pages_manager():
    def __init__(self, oled: SSD1306_I2C,
                rotary_encoder: RotaryIRQ,
                select_button: Pin) -> None:
        self.pages=list()
        self.target_page=None
        self.actual_encoder_value=int()
        self.oled=oled
        self.rotary_encoder=rotary_encoder
        self.select_button=select_button

    def add_page(self,
                page_id: int,
                entries:list,
                cursor=">", 
                right_cursor="<", 
                cursor_default_position=0) -> None:
        self.pages.append(page())
        self.pages[-1].cursor=cursor
        self.pages[-1].right_cursor=right_cursor
        self.pages[-1].cursor_position=cursor_default_position
        self.pages[-1].id=page_id
        self.pages[-1].options_lines=entries

    def __display_page(self, spacing=11) -> None:
        self.oled.fill(0)
        line_increment=0
        if self.actual_encoder_value>5:
            line_increment=self.actual_encoder_value-5
        display_lines=self.target_page.page_lines[line_increment:line_increment+6]
        print(display_lines)
        raw_counter=int()
        for line in display_lines:
            if line.strip()!="":
                self.oled.text(line, 0, raw_counter)
                raw_counter+=spacing
        self.oled.show()

    def __change_page(self, actual_page: page, cursor_position: int) -> None:
        if actual_page==self.pages[0]:
            self.target_page=self.pages[cursor_position+1]
        if cursor_position==5:
            self.target_page=self.pages[0]

    def loop(self) -> None:
        self.target_page=self.pages[0]
        while True:
            last_encoder_value=self.rotary_encoder.value()
            sleep(0.15)
            self.actual_encoder_value=self.rotary_encoder.value()
            self.target_page.cursor_position=self.actual_encoder_value
            self.target_page.build_page()
            if self.actual_encoder_value!=last_encoder_value:
                self.__display_page()
            if not self.select_button.value():
                self.__change_page(self.target_page, self.actual_encoder_value)