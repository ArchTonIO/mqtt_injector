"""
This module contains the page class,
the fundamental unit of the menu.
"""


class Page():
    """
    This class is used to represent a page.
    A page is basically a list of options
    that can be selected.
    """
    def __init__(self):
        self.uid = ""
        self.cursor = ""
        self.right_cursor = ""
        self.cursor_position = 0
        self.options = []
        self.__lines = []
        self.parent = None
        self.childs = {}

    def build_page(self, cursors_at_screen_border=False) -> None:
        """
        This method is used to build the page.
        Building the page means to add the cursor and spaces
        around the selected option.
        Page lines differs from options lines cause they contains
        the cursor.
        - Args:
            - cursors_at_screen_border, default False:
                - True:
                    ___________________
                    |     option_0    |
                    | >   option_1  < |
                    |     option_2    |
                    |_________________|
                - False:
                    ___________________
                    |     option_0    |
                    |    >option_1<   |
                    |     option_2    |
                    |_________________|
        """
        if (
            "back" in self.options
            and self.options.index("back") != len(self.options) - 1
        ):
            raise ValueError("bad position for 'back', place it as last entry")
        self.__lines = [None]*len(self.options)
        for i, option in enumerate(self.options):
            if i == self.cursor_position:
                num_spaces = int(
                    (16 - (len(self.cursor) + len(option))) / 2
                )
                spaces = " " * num_spaces
                if len(option) % 2 != 0:
                    spaces = " " * (num_spaces-1)
                if cursors_at_screen_border:
                    self.__lines[i] = (
                        self.cursor
                        + spaces
                        + option
                        + spaces
                        + self.right_cursor
                    )
                else:
                    self.__lines[i] = (
                        spaces
                        + self.cursor
                        + option
                        + self.right_cursor
                        + spaces)
            else:
                num_spaces = int((16-len(option))/2)
                spaces = " "*num_spaces
                self.__lines[i] = spaces+self.options[i]+spaces

    def print_page(self) -> None:
        """
        This method is used to print the page.
        """
        self.build_page()
        for line in self.__lines:
            print(line)
