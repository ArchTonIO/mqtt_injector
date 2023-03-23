"""
This module is used to manage the pages of the menu.
"""

import json
from page import Page
from data_page import DataPage


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
            PMan.add_page(
                page_uid=menu[key]["__page_uid"],
                entries=entries,
                parent=menu[key]["__parent"],
                childs=menu[key]["__childs"],
                cursor=menu[key]["__cursor"],
                right_cursor=menu[key]["__right_cursor"],
                cursor_default_position=menu[key]["__cursor_default_position"],
            )
            PMan.back_positions.append((menu[key]["__page_uid"], len(entries)))
            PMan.target_page = PMan.pages["A0"]
        print("done")

    @staticmethod
    def add_page(
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

    @staticmethod
    def destroy_last_page() -> None:
        """
        This method is used to destroy the last page of the menu.
        """
        PMan.pages.pop(-1)
        PMan.back_positions.pop(-1)


PMan.build_menu_from_json(json_file="settings/pages.json")
