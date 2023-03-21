"""
This file contains the commands to be executed when a button is pressed.
"""


class CommandDispatcher:
    """
    Dispatch commands to the different commands modules.
    """
    def __init__(self):
        self.commands = {
            (1, 0): "wlan scan",
            (1, 1): "wlan status",
            (1, 2): "wlan connect",
            5: "wlan insert password",
            (3, 0): "fast publish",
            (3, 1): "fast connect",
            (3, 2): "mqtt set_conn",
            (3, 3): "mqtt connect",
            (3, 4): "mqtt status",
            (3, 5): "mqtt subscribe",
            (3, 6): "mqtt publish",
            (4, 0): "mount card",
            (4, 1): "umount card",
            (4, 2): "list files",
            67: "read file",
            (4, 3): "format card",
            (4, 4): "read log",
            (4, 5): "write file",
            (4, 6): "excecute file",
        }

    def dispatch(self, pages_manager, target_page, cursor_position):
        """
        This method is used to execute the commands.
        It calls the appropriate method based on the page id.
        - Args:
            - page_cursor_key: a tuple containing the page id
        """
        if (
            target_page == 1
            or cursor_position == 5
        ):
            page_cursor_key = (target_page, cursor_position)
            self.execute_wifi_commands(
                pages_manager,
                page_cursor_key
            )
        elif target_page == 3:
            page_cursor_key = (target_page, cursor_position)
            self.execute_mqtt_commands(
                pages_manager,
                page_cursor_key
            )
        elif target_page == 4:
            page_cursor_key = (target_page, cursor_position)
            self.execute_sd_commands(
                pages_manager,
                page_cursor_key
            )
