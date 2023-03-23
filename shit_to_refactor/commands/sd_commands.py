"""
This module contains the commands related to the sd card.
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
from time import sleep
from commands.commands_dispatcher import CommandDispatcher
from hardware_manager import HwMan


class SdCommands(CommandDispatcher):
    """
    This class is used to manage the sd card commands.
    """
    def __init__(self):
        self.commands = super.commands
        self.pages_manager = super.pages_manager
        self.hw_man = HwMan

    def exec(
        self,
        pages_manager,
        page_cursor_key: tuple
    ) -> None:
        """
        This method is used to execute the commands
        related to the sd card.
        - Args:
            - pages_manager: the pages manager object.
            - page_cursor_key: a tuple containing the page id
                and the cursor position.
        """
        if self.commands[page_cursor_key] == "mount card":
            self.__mount_umount(operation="mount")

        elif self.commands[page_cursor_key] == "unmount card":
            self.__mount_umount(operation="umount")
        elif self.commands[page_cursor_key] == "list files":
            self.hw_man.oled.fill(0)
            self.hw_man.oled.text("listing files...", 0, 0)
            self.hw_man.oled.show()
            sleep(1)
            self.hw_man.oled.fill(0)
            entries = self.hw_man.list_sd_card_files()
            if entries != []:
                entries.append("back")
                pages_manager.add_page(
                    page_id="67",
                    entries=entries,
                    is_leaf=False,
                )
                pages_manager.target_page = pages_manager.pages[-1]
                pages_manager.__display_page()
            else:
                self.hw_man.oled.text("no files found!", 0, 0)
                self.hw_man.oled.show()
                sleep(2)
                pages_manager.target_page = pages_manager.pages[4]
                pages_manager.__display_page()
        elif self.commands[page_cursor_key[0]] == "read file":
            file_list = self.hw_man.retrieve_file_list()
            entries = list(
                self.hw_man.read_from_sd_card(
                    file_name=file_list[page_cursor_key[1]])
            )
            entries.append("back")
            pages_manager.add_page(
                page_id="68",
                entries=entries,
                is_leaf=True,
                cursor="|",
                right_cursor=""
            )
            pages_manager.target_page = pages_manager.pages[-1]
            pages_manager.__display_page()
        elif self.commands[page_cursor_key] == "write file":
            file_name = self.hw_man.write_from_keyboard_to_oled(
                initial_text="file name: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
            file_content = self.hw_man.write_from_keyboard_to_oled(
                initial_text="file content: ",
                exit_text="got it!",
                abort_tex="exiting..."
            )
            self.hw_man.write_to_sd_card(
                file_name=file_name,
                file_content=file_content
            )
            pages_manager.target_page = pages_manager.pages[4]
            pages_manager.__display_page()

    def __mount_umount(self, operation: str) -> None:
        self.hw_man.oled.fill(0)
        if operation == "mount":
            if self.hw_man.mount_card():
                self.hw_man.oled.text("card mounted!", 0, 0)
            else:
                self.hw_man.oled.text("cannot mount card!", 0, 0)
        elif operation == "umount":
            if self.hw_man.unmount_card():
                self.hw_man.oled.text("card unmounted!", 0, 0)
            else:
                self.hw_man.oled.text("cannot unmount card!", 0, 0)
            self.hw_man.oled.show()
        sleep(2)
        self.pages_manager.target_page = self.pages_manager.pages[4]
        self.pages_manager.__display_page()
