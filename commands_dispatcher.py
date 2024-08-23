""" Dispatch the commands to the right manager. """
from commands import (
    WlanManager,
    BleManager,
    MqttManager,
    SdManager,
    ConfigManager
)
from hardware_manager import HardwareManager


class CommandsDispatcher:
    """
    Dispatch the commands to the right manager.

    Attributes
    ----------
    HardwareManager : an instance of the HardwareManager class.
    wlan_manager : an instance of the WlanManager class.
    ble_manager : an instance of the BleManager class.
    mqtt_manager : an instance of the MqttManager class.
    sd_manager : an instance of the SdManager class.
    config_manager : an instance of the ConfigManager class.
    commands : a dict containing the commands.
    """
    def __init__(self, hw_man: HardwareManager) -> None:
        self.hw_man = hw_man
        self.sd_manager = SdManager(hw_man, self.add_command)
        self.wlan_manager = WlanManager(hw_man, self.add_command)
        self.ble_manager = BleManager(self.add_command)
        self.mqtt_manager = MqttManager(self.add_command)
        self.config_manager = ConfigManager(hw_man, self.add_command)
        self.commands = {}
        self._bind_commands()
        self.command_output_to_display = {}

    def _bind_commands(self) -> None:
        """ Bind the commands to the right manager. """
        self.commands = {
            "screen off": self.hw_man.screen_off,
            "wlan scan": self.wlan_manager.scan_networks,
            "wlan status": self.wlan_manager.status,
            "list devices": self.wlan_manager.list_devices,
            "disconnect": self.wlan_manager.disconnect,
            "ble status": self.ble_manager.status,
            "ble scan": self.ble_manager.scan,
            "ble connect": self.ble_manager.connect,
            "fast_publish": self.mqtt_manager.fast_publish,
            "fast_connect": self.mqtt_manager.connect,
            "mqtt set conn": self.mqtt_manager.create_connection,
            "mqtt connect": self.mqtt_manager.connect,
            "mqtt status": self.mqtt_manager.status,
            "mqtt subscribe": self.mqtt_manager.subscribe,
            "mqtt publish": self.mqtt_manager.publish,
            "mount card": self.sd_manager.mount_card,
            "umount card": self.sd_manager.unmount_card,
            "list files": self.sd_manager.list_card_files,
            "format card": self.sd_manager.format_card,
            "read log": self.sd_manager.read_log_file,
            "excecute file": self.sd_manager.excecute_file,
            "boot hw check": self.config_manager.set_boot_hardware_check,
            "boot animation": self.config_manager.set_boot_animation,
            "error recovery": self.config_manager.set_error_recovery,
            "led brightness": self.config_manager.set_led_brightness,
            "oled brightnes": self.config_manager.set_oled_brightness,
            "oled contrast": self.config_manager.set_oled_contrast,
            "rverse encoder": self.config_manager.set_encoder_reverse,
            "save to flash": self.config_manager.save_config,
            "available sram": self.config_manager.get_available_sram,
            "availble flash": self.config_manager.get_available_flash,
            "sram leds: on": self.config_manager.enable_available_sram_led_indicator,
            "sram leds: off": self.config_manager.disable_available_sram_led_indicator,
        }

    def add_command(self, command: str, callback, args: list) -> None:
        """
        Add a command to the commands dict.

        Parameters
        ----------
        command : str, the command to add.
        callback : the callback to add.
        """
        self.commands[command] = (callback, args)

    def dispatch(
        self,
        page_uid: str,
        repr_command: str
    ) -> None | dict:
        """
        Dispatch the command to the corresponding manager.

        Parameters
        ----------
        page_uid : str, the actual page uid.
        repr_command : str, the command to dispatch.
        args : list, the arguments of the command.
        """
        callback = self.commands.get((repr_command))
        if callback is None:
            return
        if isinstance(callback, tuple):
            callback, args = callback
            return callback(*args)
        return callback()

