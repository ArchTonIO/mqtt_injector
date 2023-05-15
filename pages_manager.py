"""
This module is used to manage the pages of the menu.
"""
# pylint: disable=import-error
import json
from time import sleep
from machine import Pin
from ssd1306 import SSD1306_I2C
from page import Page, DataPage
from rotary. rotary_irq_pico import RotaryIRQ


class PagesManager():
    """
    This class is used to manage the pages of the menu.
    """
    def __init__(
        self,
        encoder: RotaryIRQ,
        select_button: Pin,
        oled: SSD1306_I2C
    ) -> None:
        self.encoder = encoder
        self.select_button = select_button
        self.oled = oled
        self.pages = {}
        self.target_page = None
        self.back_positions = []
        self.last_encoder_value = 0

    def build_menu_from_json(self, json_file: str) -> None:
        """
        Build the device menu by parsing the pages json.
        """
        with open(json_file, "r", encoding="UTF-8") as file:
            menu = json.load(file)
        ordered_keys = self._order_menu_keys(menu)
        for key in ordered_keys:
            entries = self._parse_entries(menu[key].keys(), menu[key])
            self._add_page(
                page_uid=menu[key]["__page_uid"],
                entries=entries,
                parent=menu[key]["__parent"],
                childs=menu[key]["__childs"],
                cursor=menu[key]["__cursor"],
                right_cursor=menu[key]["__right_cursor"],
                cursor_default_position=menu[key]["__cursor_default_position"]
            )
            if menu[key]["__parent"] == "none":
                continue
            self.back_positions.append(
                (menu[key]["__page_uid"], len(entries)-1))

    def _order_menu_keys(self, menu) -> list:
        """
        Since the json parser doesn't keep the order of the keys,
        this function is used to order the keys by parsing order.
        """
        ordered_keys = []
        last_parsing_order = 0
        while len(ordered_keys) < len(list(menu.keys())):
            for key in menu.keys():
                actual_parsing_order = int(menu[key]["__parsing_order"])
                if actual_parsing_order - last_parsing_order != 1:
                    continue
                last_parsing_order = actual_parsing_order
                ordered_keys.append(key)
        return ordered_keys

    def _parse_entries(self, keys: list, page: dict) -> list:
        """
        Parse in an ordered way the entries of the menu.
        """
        entries = [(int(key), page[key]) for key in keys if "__" not in key]
        sorted_entries = sorted(entries, key=lambda x: x[0])
        return [entry[1] for entry in sorted_entries]

    def _add_page(
        self,
        page_uid: int,
        entries: list,
        parent: str,
        childs: dict,
        cursor: str,
        right_cursor: str,
        cursor_default_position: str
    ) -> None:
        """
        This function is used to add a page to the menu.
        Adding means appending to the pages list.
        - Params:
            - page_uid: the page id.
            - entries: the entries (options) of the page.
            - cursor: the character used as cursor.
            - right_cursor: the character used as right cursor.
            - cursor_default_position: the default position
                of the cursor when the knob is not turned.
        """
        self.pages.update({page_uid: Page(self.oled)})
        self.pages[page_uid].uid = page_uid
        self.pages[page_uid].cursor = cursor
        self.pages[page_uid].right_cursor = right_cursor
        self.pages[page_uid].cursor_position = int(cursor_default_position)
        self.pages[page_uid].options = entries
        self.pages[page_uid].parent = parent
        self.pages[page_uid].childs = childs

    def _switch_page(self, current_page: str, selected_option: int) -> None:
        """
        This function is used to switch the current page
        to the target page (from parent to child or viceversa).
        """
        if (current_page.uid, selected_option) in self.back_positions:
            self.target_page = self.pages[current_page.parent]
            return
        self.target_page = self.pages[
            current_page.childs[
                str(selected_option)
            ]
        ]

    def display_data_page(self, data: list) -> None:
        """
        This function is used to display a data page.
        - Params:
            - data: the data to display (a list of strings).
        """
        data_page = DataPage(data)
        data_page.to_oled()

    def destroy_last_page(self) -> None:
        """
        This method is used to destroy the last page of the menu.
        """
        self.pages.pop(-1)
        self.back_positions.pop(-1)

    def _setup(self) -> None:
        """ Setup the first page to be displayed on the menu. """
        self.last_encoder_value = self.encoder.value()
        self.target_page = self.pages["A0"]
        self.encoder.max_val = len(self.target_page.options) - 1
        self.target_page.to_oled()

    def _loop(self) -> None:
        """ Loop the menu. """
        if self.encoder.value() != self.last_encoder_value:
            self.last_encoder_value = self.encoder.value()
            self.target_page.cursor_position = self.encoder.value()
            self.target_page.to_oled()
        if self.select_button.value() == 0:
            self._perform_action()

    def _perform_action(self):
        """ Perform one of the two actions:
            - switch page
            - excecute command
            This is decided by the presence of childs in the target page
            and by the presence of the target page in the back_positions list,
            it is given that if the target page has no childs, it has to
            excecute a command.
        """
        if (
            (
                self.target_page.uid, self.encoder.value()
            ) not in self.back_positions
            and self.target_page.childs == {}
        ):
            self._excecute_command()
            return
        self._switch_page(self.target_page, self.encoder.value())
        self.encoder.max_val = len(self.target_page.options) - 1
        self.target_page.to_oled()
        sleep(0.2)

    def _excecute_command(self):
        print(
            "if you see this, you have to implement the"
            " _excecute_command method"
        )

    def run(self) -> None:
        """ Kick off the menu. """
        self._setup()
        while True:
            self._loop()
