""" Manage the pages of the menu. """
import json
from time import sleep

from machine import Pin
from ssd1306 import SSD1306_I2C

from commands_dispatcher import CommandsDispatcher
import logger
from page import Page, DataPage
from rotary. rotary_irq_pico import RotaryIRQ


class PagesManager:
    """
    Manage the pages of the menu.

    Attributes
    ----------
    encoder : the rotary encoder
    select_button : the select button
    oled : the oled display
    commands_dispatcher : the commands dispatcher instance
    """
    def __init__(
        self,
        encoder: RotaryIRQ,
        select_button: Pin,
        oled: SSD1306_I2C,
        commands_dispatcher: CommandsDispatcher
    ) -> None:
        self.encoder = encoder
        self.select_button = select_button
        self.oled = oled
        self.commands_dispatcher = commands_dispatcher
        self.pages = {}
        self.target_page: Page =  None
        self.back_positions = []
        self.last_encoder_value = 0

    def build_menu_from_dict(self, menu: dict) -> None:
        """
        Build the device menu by parsing the pages json.

        Parameters
        ----------
        menu : the menu dict.
        """
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

    def _order_menu_keys(self, menu: dict) -> list:
        """
        Since the json parser doesn't keep the order of the keys,
        this function is used to order the keys by parsing order.

        Parameters
        ----------
        menu : the menu dict.
        """
        ordered_keys = []
        last_parsing_order = 0
        while len(ordered_keys) < len(list(menu.keys())):
            for key in menu:
                actual_parsing_order = int(menu[key]["__parsing_order"])
                if actual_parsing_order - last_parsing_order != 1:
                    continue
                last_parsing_order = actual_parsing_order
                ordered_keys.append(key)
        return ordered_keys

    def _parse_entries(self, keys: list, page: dict) -> list:
        """
        Parse in an ordered way the entries of the menu.

        Parameters
        ----------
        keys : the keys of the page dict.
        page : the page dict.

        Returns
        -------
        list : the ordered entries list.
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
        """
        self.pages.update({page_uid: Page(self.oled)})
        self.pages[page_uid].uid = page_uid
        self.pages[page_uid].cursor = cursor
        self.pages[page_uid].right_cursor = right_cursor
        self.pages[page_uid].cursor_position = int(cursor_default_position)
        self.pages[page_uid].options = entries
        self.pages[page_uid].parent = parent
        self.pages[page_uid].childs = childs

    def _switch_page(self, current_page: Page, selected_option: int) -> None:
        """
        This function is used to switch the current page
        to the target page (from parent to child or viceversa).

        Parameters
        ----------
        current_page : the page currently displayed.
        selected_option : the selected option index of the current page.
        """
        if (current_page.uid, selected_option) in self.back_positions:
            self.target_page = self.pages[current_page.parent]
            return
        self.target_page = self.pages[
            current_page.childs[
                str(selected_option)
            ]
        ]

    def display_data_page(self, data: list, persistence: int = 3) -> None:
        """
        This function is used to display a data page,
        which is a page that displays a bunch of strings without any cursor,
        after the specified amount of time the page is replaced by the
        previous one.

        Parameters
        ----------
        data : the data to display (a list of strings).
        persistence : the time in seconds the page will be displayed
        before destroying it.
        """
        data_page = DataPage(data, self.oled)
        data_page.to_oled()
        sleep(persistence)
        self.target_page.to_oled()

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
        logger.log(
            "[PAGES MANAGER]: "
            f"the page {self.target_page.uid} has been displayed"
        )

    def _loop(self) -> None:
        """ Loop the menu. """
        if self.encoder.value() != self.last_encoder_value:
            self.last_encoder_value = self.encoder.value()
            self.target_page.cursor_position = self.encoder.value()
            self.target_page.to_oled()
            logger.log(
                "[PAGES MANAGER]: "
                f"the page {self.target_page.uid} has been displayed"
            )
        if self.select_button.value() == 0:
            self._perform_action()

    def _perform_action(self) -> None:
        """
        Perform one of the two actions:
        - : switch page
        - : excecute command
        This is choosen by the presence of childs in the target page
        and by the presence of the target page in the back_positions list,
        it is given that if the target page has no childs, it must
        excecute a command.
        """
        if (
            (
                self.target_page.uid, self.encoder.value()
            ) not in self.back_positions
            and self.target_page.childs == {}
        ):
            self._excecute_command(self.target_page, self.encoder.value())
            return
        self._switch_page(self.target_page, self.encoder.value())
        self.encoder.max_val = len(self.target_page.options) - 1
        self.target_page.to_oled()
        sleep(0.2)

    def _excecute_command(self, target_page, encoder_value: int) -> None:
        """
        Excecute a command.

        Parameters
        ----------
        target_page : the target page.
        encoder_value : the encoder value.
        """
        return_value = self.commands_dispatcher.dispatch(
            page_uid=target_page.uid,
            cursor_position=encoder_value
        )
        print(return_value)
        self._create_pages_from_command_return_value(return_value)

    def _create_pages_from_command_return_value(self, return_value) -> None:
        """
        Create pages from the return value of the command.
        The return value can be a dict or a list.
        - : If it is a dict, it means that the command has created a page
        and the page has to be added to the menu.
        - : If it is a list, it means that the command has to display a
        data page.
        """
        if isinstance(return_value, dict):
            return_value["entries"].append("back")
            self._add_page(
                page_uid=return_value["page_uid"],
                entries=return_value["entries"],
                parent=return_value["parent"],
                childs=return_value["childs"],
                cursor=return_value["cursor"],
                right_cursor=return_value["right_cursor"],
                cursor_default_position=return_value[
                    "cursor_default_position"
                ]
            )
            self.target_page = self.pages[return_value["page_uid"]]
            self.back_positions.append(
                (return_value["page_uid"], len(return_value["entries"])-1)
            )
            self.encoder.max_val = len(self.target_page.options) - 1
            self.target_page.to_oled()
        if isinstance(return_value, list):
            self.display_data_page(return_value)

    def run(self, recovery_from_exceptions = True) -> None:
        """ Start the menu execution. """
        self._setup()
        while True:
            try:
                self._loop()
            except Exception as e:
                if not recovery_from_exceptions:
                    raise e
                logger.log(
                    "[PAGES MANAGER]: "
                    f"an exception has been raised: {e}"
                )
                self.display_data_page(
                    [
                        "__ERROR__", 
                        "restarting..."
                    ]
                )
                self.run(recovery_from_exceptions)
