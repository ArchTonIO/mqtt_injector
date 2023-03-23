"""
This module contains the page class,
the fundamental unit of the menu.
"""
#  from hardware_manager import HwMan


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
        self.parent = None
        self.childs = {}
        self.__lines = []
        self.__MAX_CHARS_PER_LINE_ON_OLED = 16
        self.__MAX_LINES_ON_OLED = 6
        self.__OLED = 0  # HwMan.oled

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
        self.__check_back_position()
        self.__lines = [None]*len(self.options)
        for i, option in enumerate(self.options):
            self.__check_option_length(option)
            if i != self.cursor_position:
                self.__build_line_with_no_cursor(option, i)
                continue
            self.__build_line_with_cursor(option, cursors_at_screen_border, i)

    def __check_back_position(self) -> None:
        """
        Check if the back option is placed at the last position of the page.
        """
        if (
            "back" in self.options
            and self.options.index("back") != len(self.options) - 1
        ):
            raise ValueError("bad position for 'back', place it as last entry")

    def __check_option_length(self, option: str) -> None:
        """
        Check if the option length is greater than the maximum
        number of characters per line.
        """
        if len(option) > self.__MAX_CHARS_PER_LINE_ON_OLED:
            raise ValueError(
                f"option: {option} is too long to fit the screen"
                "please reduce it to a maximum of "
                f"{self.__MAX_CHARS_PER_LINE_ON_OLED - len(self.cursor) * 2}"
                " characters"
            )

    def __build_line_with_cursor(self, option, cursors_at_screen_border, i):
        """
        This method is used to build a line with the cursor.
        """
        num_spaces = int(
            (
                self.__MAX_CHARS_PER_LINE_ON_OLED - (
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
            self.__populate_line_witch_adjacent_cursor(option, spaces, i)
            return
        self.__populate_line_with_cursor_at_screen_border(option, spaces, i)

    def __populate_line_witch_adjacent_cursor(self, option, spaces, i):
        """
        This method is used to populate a line with the cursor adjacent
        to the option.
        """
        self.__lines[i] = (
            spaces
            + self.cursor
            + option
            + self.right_cursor
            + spaces
        )

    def __populate_line_with_cursor_at_screen_border(self, option, spaces, i):
        """
        This method is used to populate a line with the cursor at the
        screen border.
        """
        self.__lines[i] = (
            self.cursor
            + spaces
            + option
            + spaces
            + self.right_cursor
        )

    def __build_line_with_no_cursor(self, option, i):
        """
        This method is used to build a line with no cursor.
        """
        num_spaces = int((self.__MAX_CHARS_PER_LINE_ON_OLED-len(option))/2)
        spaces = " "*num_spaces
        self.__lines[i] = spaces+self.options[i]+spaces

    def update_cursor_row_position(self, position) -> None:
        position = len(self.options) - 1 if position < 0 else position
        position = 0 if position > len(self.options) - 1 else position
        self.cursor_position = position

    def print_page(self) -> None:
        """
        This method is used to print the page.
        """
        self.build_page()
        for line in self.__lines:
            print(line)

    def page_to_oled(
        self,
        lines_spacing: int = 11,
        lines_creation_interval: float = 0
    ) -> None:
        """
        Print the page to the oled display.
        - Params:
            - lines_spacing: the spacing between the lines in pixels
            - lines_creation_interval: the interval between the lines
                creation in seconds, if greater than 0 the lines will
                be created one by one and you will see them be written
                gradually on the screen.
        """
        display_lines = self.__concretize_page()
        self.__show_on_oled(
            display_lines,
            lines_spacing,
            lines_creation_interval
        )

    def __concretize_page(self) -> None:
        """
        Make the page lines fits the oled display.
        """
        line_increment = 0
        if self.cursor_position > self.__MAX_LINES_ON_OLED - 1:
            line_increment = (
                self.cursor_position - self.__MAX_LINES_ON_OLED - 1
            )
        return self.__lines[
            line_increment: line_increment + self.__MAX_LINES_ON_OLED
        ]

    def __show_on_oled(self, display_lines: list) -> None:
        """
        Show the page on the oled display.
        """
        self.OLED.fill(0)
        row_counter = 0
        for line in display_lines:
            self.OLED.text(line, 0, row_counter)
            row_counter += lines_spacing
            if lines_creation_interval > 0:
                self.OLED.show()
                time.sleep(lines_creation_interval)
        self.OLED.show()
