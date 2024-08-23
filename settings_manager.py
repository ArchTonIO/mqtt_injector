""" Manage the settings of the device. """
import json
import os

from device_logging import Logger


class SettingsManager:
    """ Load and read the settings of the application. """

    settings_dict: dict = {}
    logger = Logger("SETTINGS_MANAGER")

    @staticmethod
    def isfile(path: str) -> bool:
        """
        Return True if the path is a file, False otherwise.

        Parameters
        ----------
        path : str, the path to check.
        """
        return os.stat(path)[0] & 0o170000 == 0o100000

    @classmethod
    def load_settings(cls, source_dir: str = "settings") -> None:
        """
        Load the settings from the settings file.

        Parameters
        ----------
        source_dir : str, the path to the settings folder.
        """
        cls.settings_dict = {}
        for settings_file in os.listdir(source_dir):
            file_stem = settings_file.split(".")[0]
            file_suffix = settings_file.split(".")[-1]
            if (
                cls.isfile(f"{source_dir}/{settings_file}")
                and file_suffix == "json"
            ):
                cls.logger.info(f"correctly loaded {settings_file}")
                with open(
                    f"{source_dir}/{settings_file}", "r", encoding="utf-8"
                ) as current_file:
                    cls.settings_dict[file_stem] = json.load(
                        current_file
                    )
            else:
                cls.logger.warning(
                    f"[SETTINGS MANAGER]: cannot load {settings_file}"
                )

    @classmethod
    def get_settings(cls, file_name: str = "") -> dict:
        """
        Return the content of the settings file.

        Parameters
        ----------
        source_dir : str, the path to the settings folder.
        file_name : str, the name of the settings file.

        Returns
        -------
        dict : the content of the settings file.
        """
        if not file_name:
            return cls.settings_dict
        if file_name not in cls.settings_dict:
            cls.logger.error(f"{file_name}, file not found.")
            raise ValueError(f"{file_name}, file not found.")
        return cls.settings_dict[file_name]

    @classmethod
    def save_settings(cls) -> bool:
        """
        Save the settings to the settings dir.
        Returns
        -------
        bool : True if the settings are saved, False otherwise.
        """
        for file_name in cls.settings_dict:
            with open(
                f"settings/{file_name}.json", "w", encoding="utf-8"
            ) as current_file:
                json.dump(
                    cls.settings_dict[file_name],
                    current_file,
                    indent=4,
                )
        return True
