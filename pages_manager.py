"""
This module is used to manage the pages of the menu.
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=too-many-instance-attributes
from time import sleep

from machine import Pin
from ssd1306 import SSD1306_I2C

from commands import command_executer
from page import page
from rotary.rotary_irq_pico import RotaryIRQ


class PagesManager():
    """
    This class organizes the pages into a menu.
    """
    def __init__(
        self,
        oled: SSD1306_I2C,
        rotary_encoder: RotaryIRQ,
        select_button: Pin
    ) -> None:
        self.pages = []
        self.target_page = None
        self.actual_encoder_value = int()
        self.oled = oled
        self.rotary_encoder = rotary_encoder
        self.select_button = select_button
        self.back_positions = []
        self.off_pos = 6
        self.cmd_executer = command_executer()

    def add_page(
        self,
        page_id: int,
        entries: list,
        cursor=">",
        right_cursor="<",
        cursor_default_position=0,
    ) -> None:
        """
        This method is used to add a page to the menu.
        - Args:
            - page_id: the page id.
            - entries: the entries (options) of the page.
            - cursor: the character used as cursor.
            - right_cursor: the character used as right cursor.
            - cursor_default_position: the default position
                of the cursor when the knob is not turned.
        - Returns:
            None.
        """
        self.pages.append(page())
        self.pages[-1].cursor = cursor
        self.pages[-1].right_cursor = right_cursor
        self.pages[-1].cursor_position = cursor_default_position
        self.pages[-1].id = page_id
        self.pages[-1].options_lines = entries
        self.back_positions.append((page_id,
                                    entries.index("back")))

    def destroy_last_page(self) -> None:
        """
        This method is used to destroy the last page of the menu.
        - Args:
            - None.
        - Returns:
            - None.
        """
        self.pages.pop(-1)
        self.back_positions.pop(-1)

    def __display_page(self, spacing=11) -> None:
        """
        This method is used to display the current page.
        - Args:
            - spacing: the vertical spacing between
                the lines (in pixels), default is 11.
        - Returns:
            - None.
        """
        self.oled.fill(0)
        line_increment = 0
        if self.actual_encoder_value > 5:
            line_increment = self.actual_encoder_value-5
        display_lines = (
            self.target_page.page_lines[line_increment:line_increment+6]
        )
        raw_counter = int()
        for line in display_lines:
            self.oled.text(line, 0, raw_counter)
            raw_counter += spacing
        self.oled.show()

    def __action(self) -> None:
        """
        This method is called whenever the select button is pressed.
        Its work is to execute the command associated with the
        current page and the current cursor position.
        - Args:
            - None.
        - Returns:
            - None.
        """
        if (self.target_page == self.pages[0]
                and self.actual_encoder_value == self.off_pos):
            self.oled.fill(0)
            self.oled.show()
        elif ((self.target_page.id,
                self.actual_encoder_value) in self.back_positions
                or not self.target_page.is_leaf):
            self.__change_page()
        else:
            self.cmd_executer.execute(
                self,
                (
                    self.target_page.id,
                    self.actual_encoder_value
                )
            )

    def __change_page(self) -> None:
        """
        This method is used to change the current page
        to the page associated with the current cursor position.
        - Args:
            - None.
        - Returns:
            - None.
        """
        if self.target_page == self.pages[0]:
            self.target_page = self.pages[self.actual_encoder_value+1]
        elif ((self.target_page.id, self.actual_encoder_value)
                in self.back_positions):
            self.target_page = self.pages[0]
        self.target_page.build_page()
        self.__display_page()

    def loop(self) -> None:
        """
        This method is used to start the menu loop,
        this is necessary to make the menu work.
        - Args:
            - None.
        - Returns:
            - None.
        """
        self.target_page = self.pages[0]
        self.target_page.build_page()
        self.__display_page()
        while True:
            last_encoder_value = self.rotary_encoder.value()
            sleep(0.15)
            print(self.rotary_encoder.value())
            self.target_page.cursor_position = self.actual_encoder_value
            self.target_page.build_page()
            if self.actual_encoder_value != last_encoder_value:
                self.__display_page()
            if not self.select_button.value():
                self.__action()
