"""
Data page is a page that only contains data. It is a subclass of Page.
Data pages are for their nature static and meant to be deleted after
they have been displayed.
"""
from page import Page


class DataPage(Page):
    """
    - params:
        - data: the data to show, a list of strings.
    """
    def __init__(self, data: list):
        super().__init__()
        self.data = data
        self.__MAX_LINES = 6

    def build_page(self) -> None:
        """
        This method is used to build the page.
        """
        self.__check_data()
        self._Page__lines = self.data

    def __check_data(self) -> None:
        """
        Check if the data is too long to be displayed.
        """
        self.__vertical_check()
        self.__horizontal_check()

    def __vertical_check(self) -> None:
        """
        Check if the data is too long to be displayed vertically.
        """
        if len(self.data) > self.__MAX_LINES:
            raise ValueError(
                "too many lines to be displayed, "
                "please reduce it to 6 lines"
            )

    def __horizontal_check(self) -> None:
        """
        Check if the data is too long to be displayed horizontally.
        """
        for line in self.data:
            if len(line) > self._Page__MAX_CHARS_PER_LINE:
                raise ValueError(
                    "too_many chars to be displayed, "
                    "please reduce it to 16 chars"
                )
