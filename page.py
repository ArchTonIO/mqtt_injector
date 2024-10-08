"""
This module contains the page class,
the fundamental unit of the menu.
"""
from time import sleep
from ssd1306 import SSD1306_I2C

MAX_CHARS_PER_LINE_ON_OLED = 16
MAX_LINES_ON_OLED = 6


class Page:
    """
    This class is used to represent a page.
    A page is basically a list of options
    that can be selected.

    Attributes
    ----------

    oled : the oled display
    uid : the page id
    cursor : the cursor character
    right_cursor : the right cursor character
    cursor_position : the cursor position (the line, 0 being the first)
    options : the page options
    parent : the parent page id
    childs : the child pages ids
    _lines  : the page lines
    """

    def __init__(self, oled: SSD1306_I2C):
        self.oled = oled
        self.uid = ""
        self.cursor = ""
        self.right_cursor = ""
        self.cursor_position = 0
        self.options = []
        self.parent = None
        self.childs = {}
        self._lines = []

    @property
    def lines(self) -> list:
        """
        Get the page lines.
        """
        return self._lines

    @lines.setter
    def lines(self, lines: list) -> None:
        """
        Set the page lines.
        """
        self._lines = lines

    @lines.deleter
    def line(self) -> None:
        """
        Delete the page lines.
        """
        del self._lines

    def build_page(self, cursors_at_screen_border: bool = False) -> None:
        """
        Build the page.
        Building the page means to add the cursor and spaces
        around the selected option.
        Page lines differs from options lines cause they contains
        the cursor and the spaces.

        Parameters
        ----------
        cursors_at_screen_border : bool
        - : True:
            ___________________
            |     option_0    |
            | >   option_1  < |
            |     option_2    |
            |_________________|
        - : False:
            ___________________
            |     option_0    |
            |    >option_1<   |
            |     option_2    |
            |_________________|
        """
        self._check_back_position()
        self._lines = [None]*len(self.options)
        for i, option in enumerate(self.options):
            self._check_option_length(option)
            if i != self.cursor_position:
                self._build_line_with_no_cursor(option, i)
                continue
            self._build_line_with_cursor(option, cursors_at_screen_border, i)

    def _check_back_position(self) -> None:
        """
        Check if the back option is placed at the last position of the page.
        """
        if (
            "back" in self.options
            and self.options.index("back") != len(self.options) - 1
        ):
            raise ValueError(
                "bad position for 'back', place it as last entry",
                f"entries are: {self.options}"
            )

    def _check_option_length(self, option: str) -> None:
        """
        Check if the option length is greater than the maximum
        number of characters per line.
        """
        if len(option) > MAX_CHARS_PER_LINE_ON_OLED:
            raise ValueError(
                f"option: {option} is too long to fit the screen",
                "please reduce it to a maximum of ",
                f"{MAX_CHARS_PER_LINE_ON_OLED - len(self.cursor) * 2}"
                " characters"
            )

    def _build_line_with_cursor(
        self,
        option: str,
        cursors_at_screen_border: bool,
        i: int
    ) -> None:
        """
        Build a line with the cursor.
        """
        num_spaces = int(
            (
                MAX_CHARS_PER_LINE_ON_OLED - (
                    len(self.cursor) + len(option)
                )
            ) / 2
        )
        spaces = (
            " " * (num_spaces-1)
            if len(option) % 2 != 0
            else " " * num_spaces
        )
        if not cursors_at_screen_border:
            self._populate_line_witch_adjacent_cursor(option, spaces, i)
            return
        self._populate_line_with_cursor_at_screen_border(option, spaces, i)

    def _populate_line_witch_adjacent_cursor(
        self,
        option: str,
        spaces: str,
        i: int
    ) -> None:
        """
        Populate a line with the cursor adjacent to the option.
        """
        self.lines[i] = (
            spaces
            + self.cursor
            + option
            + self.right_cursor
            + spaces
        )

    def _populate_line_with_cursor_at_screen_border(
        self,
        option: str,
        spaces: str,
        i: int
    ) -> None:
        """
        Populate a line with the cursor at the screen border.
        """
        self.lines[i] = (
            self.cursor
            + spaces
            + option
            + spaces
            + self.right_cursor
        )

    def _build_line_with_no_cursor(self, option: str, i: int) -> None:
        """
        This method is used to build a line with no cursor.
        """
        num_spaces = int((MAX_CHARS_PER_LINE_ON_OLED - len(option)) / 2)
        spaces = " " * num_spaces
        self.lines[i] = spaces + self.options[i] + spaces

    def print_page(self) -> None:
        """
        Print the page to the console.
        """
        self.build_page()
        for line in self.lines:
            print(line)

    def to_oled(
        self,
        lines_spacing: int = 11,
        lines_creation_interval: float = 0,
        console_print: bool = False
    ) -> None:
        """
        Print the page to the oled display.

        Parameters
        ----------
        lines_spacing : the spacing between the lines in pixels
        lines_creation_interval : the interval between the lines
        creation in seconds, if greater than 0 the lines will
        be created one by one and you will see them be written
        gradually on the screen.
        console_print : if True the page will also be printed to the
        console
        """
        if console_print:
            self.print_page()
        else:
            self.build_page()
        display_lines = self._concretize_page()
        self._show_on_oled(
            display_lines,
            lines_spacing,
            lines_creation_interval
        )

    def _concretize_page(self) -> list:
        """
        Make the page lines fits the oled display vertically.
        """
        line_increment = 0
        if self.cursor_position > MAX_LINES_ON_OLED - 1:
            line_increment = self.cursor_position
        return self._lines[
            line_increment: line_increment + MAX_LINES_ON_OLED
        ]

    def _show_on_oled(
        self,
        display_lines: list,
        lines_spacing: int,
        lines_creation_interval: float
    ) -> None:
        """
        Show the page on the oled display.
        """
        self.oled.fill(0)
        row_counter = 0
        for line in display_lines:
            self.oled.text(line, 0, row_counter)
            row_counter += lines_spacing
            if lines_creation_interval > 0:
                self.oled.show()
                sleep(lines_creation_interval)
        self.oled.show()
