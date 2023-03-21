"""
This module is used to manage the pages of the menu.
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module

# from time import sleep
import json
from page import Page
# from commands import CommandExecuter
# from hardware_manager import HwMan

# ACTUAL_ENCODER_VALUE = 0
# OLED = HwMan.oled
# ENCODER = HwMan.encoder
# SEL_BUTTON = HwMan.select_button
# OFF_POS = 6
# cmd_executer = CommandExecuter()


class PMan():
    pages = {}
    target_page = None
    back_positions = []

    @staticmethod
    def build_menu_from_json(json_file: str) -> None:
        """
        Build the device menu by parsing the pages json.
        """
        with open(json_file, "r", encoding="UTF-8") as file:
            menu = json.load(file)
        for key in menu.keys():
            entries = [
                entry for entry in menu[key].keys() if "__" not in entry
            ]
            PMan.__add_page(
                page_uid=menu[key]["__page_uid"],
                entries=entries,
                parent=menu[key]["__parent"],
                childs=menu[key]["__childs"],
                cursor=menu[key]["__cursor"],
                right_cursor=menu[key]["__right_cursor"],
                cursor_default_position=menu[key]["__cursor_default_position"],
            )
            PMan.back_positions.append((menu[key]["__page_uid"], len(entries)))
        print("done")

    @staticmethod
    def __add_page(
        page_uid: int,
        entries: list,
        parent: str,
        childs: dict,
        cursor: str,
        right_cursor: str,
        cursor_default_position: str,
    ) -> None:
        """
        This funxtion is used to add a page to the menu.
        Adding means appending to the pages list.
        - params:
            - page_uid: the page id.
            - entries: the entries (options) of the page.
            - cursor: the character used as cursor.
            - right_cursor: the character used as right cursor.
            - cursor_default_position: the default position
                of the cursor when the knob is not turned.
        """
        PMan.pages.update({page_uid: Page()})
        PMan.pages[page_uid].uid = page_uid
        PMan.pages[page_uid].cursor = cursor
        PMan.pages[page_uid].right_cursor = right_cursor
        PMan.pages[page_uid].cursor_position = int(cursor_default_position)
        PMan.pages[page_uid].options = entries
        PMan.pages[page_uid].parent = parent
        PMan.pages[page_uid].childs = childs

    @staticmethod
    def switch_page(current_page: str, selected_option: int) -> None:
        """
        This function is used to switch the current page
        to the target page (from parent to child or viceversa).
        """
        if (current_page.uid, selected_option) in PMan.back_positions:
            PMan.target_page = PMan.pages[current_page.parent]
        else:
            PMan.target_page = PMan.pages[
                current_page.childs[
                    str(selected_option)
                ]
            ]


PMan.build_menu_from_json(json_file="settings/pages.json")
PMan.target_page = PMan.pages["A0"]

#     def destroy_last_page(self) -> None:
#         """
#         This method is used to destroy the last page of the menu.
#         - Args:
#             - None.
#         - Returns:
#             - None.
#         """
#         self.pages.pop(-1)
#         self.back_positions.pop(-1)

#     def __display_page(self, spacing=11) -> None:
#         """
#         This method is used to display the current page.
#         - Args:
#             - spacing: the vertical spacing between
#                 the lines (in pixels), default is 11.
#         - Returns:
#             - None.
#         """
#         self.oled.fill(0)
#         line_increment = 0
#         if self.actual_encoder_value > 5:
#             line_increment = self.actual_encoder_value-5
#         display_lines = (
#             self.target_page.page_lines[line_increment:line_increment+6]
#         )
#         raw_counter = 0
#         for line in display_lines:
#             self.oled.text(line, 0, raw_counter)
#             raw_counter += spacing
#         self.oled.show()

#     def __action(self) -> None:
#         """
#         This method is called whenever the select button is pressed.
#         Its work is to execute the command associated with the
#         current page and the current cursor position.
#         - Args:
#             - None.
#         - Returns:
#             - None.
#         """
#         if (self.target_page == self.pages[0]
#                 and self.actual_encoder_value == self.off_pos):
#             self.oled.fill(0)
#             self.oled.show()
#         elif ((self.target_page.id,
#                 self.actual_encoder_value) in self.back_positions
#                 or not self.target_page.is_leaf):
#             self.__change_page()
#         else:
#             self.cmd_executer.execute(
#                 self,
#                 self.target_page.id,
#                 self.actual_encoder_value
#             )

#     def __change_page(self) -> None:
#         """
#         This method is used to change the current page
#         to the page associated with the current cursor position.
#         - Args:
#             - None.
#         - Returns:
#             - None.
#         """
#         if self.target_page == self.pages[0]:
#             self.target_page = self.pages[self.actual_encoder_value+1]
#         elif ((self.target_page.id, self.actual_encoder_value)
#                 in self.back_positions):
#             self.target_page = self.pages[0]
#         self.target_page.build_page()
#         self.__display_page()

#     def loop(self) -> None:
#         """
#         This method is used to start the menu loop,
#         this is necessary to make the menu work.
#         - Args:
#             - None.
#         - Returns:
#             - None.
#         """
#         self.target_page = self.pages[0]
#         self.target_page.build_page()
#         self.__display_page()
#         while True:
#             last_encoder_value = self.rotary_encoder.value()
#             sleep(0.15)
#             print(last_encoder_value)
#             if self.actual_encoder_value != last_encoder_value:
#                 self.actual_encoder_value = last_encoder_value
#                 self.target_page.cursor_position = self.actual_encoder_value
#                 self.target_page.build_page()
#                 self.__display_page()
#             if not self.select_button.value():
#                 self.__action()
