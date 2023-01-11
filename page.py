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
        self.max_lines = 24
        self.cursor = str()
        self.right_cursor = str()
        self.cursor_position = int()
        self.options_lines = [str()]*self.max_lines
        self.page_lines = [str()]*self.max_lines
        self.page_id = int()

    def build_page(self, curors_at_screen_border=False) -> None:
        """
        This method is used to build the page.
        Building the page means to add the cursor
        to the selected option.
        - Args:
            - curors_at_screen_border, default False:
                - True:
                    _________________
                    |    option_0   |
                    |>   option_1  <|
                    |    option_2   |
                    |_______________|
                - False:
                    _________________
                    |    option_0   |
                    |   >option_1<  |
                    |    option_2   |
                    |_______________|
        - Returns:
            - None
        """
        for i, option in enumerate(self.options_lines):
            if i == self.cursor_position:
                num_spaces = int(
                    (16 - (len(self.cursor) + len(option))) / 2
                )
                spaces = " " * num_spaces
                if len(option) % 2 != 0:
                    spaces = " " * (num_spaces-1)
                if curors_at_screen_border:
                    self.page_lines[i] = (
                        self.cursor
                        + spaces
                        + option
                        + spaces
                        + self.right_cursor
                    )
                else:
                    self.page_lines[i] = (
                        spaces
                        + self.cursor
                        + option
                        + self.right_cursor
                        + spaces)
            else:
                num_spaces = int((16-len(option))/2)
                spaces = " "*num_spaces
                self.page_lines[i] = spaces+self.options_lines[i]+spaces

    def print_page(self, oled) -> None:
        """
        This method is used to print the page on the oled.
        - Args:
            - oled: the oled object
        - Returns:
            - None
        """
        oled.fill(0)
        for i, option in enumerate(self.page_lines):
            oled.text(option, 0, i*8)
        oled.show()
