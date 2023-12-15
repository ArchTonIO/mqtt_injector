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
    def __init__(self, h_man: HardwareManager) -> None:
        self.wlan_manager = WlanManager(h_man)
        # self.ble_manager = BleManager()
        self.mqtt_manager = MqttManager()
        self.sd_manager = SdManager(h_man)
        self.config_manager = ConfigManager()
        self.commands = {}
        self._bind_commands()
        self.command_output_to_display = {}

    def _bind_commands(self) -> None:
        """ Bind the commands to the right manager. """
        self.commands = {
            ("B0", 0): self.wlan_manager.scan_networks,
            ("B0", 1): self.wlan_manager.status,
            ("B0", 2): self.wlan_manager.connect,
            # ("C0", 0): self.ble_manager.status,
            # ("C0", 1): self.ble_manager.scan,
            # ("C0", 2): self.ble_manager.connect,
            ("D0", 0): self.mqtt_manager.fast_publish,
            ("D0", 1): self.mqtt_manager.connect,
            ("D0", 2): self.mqtt_manager.create_connection,
            ("D0", 3): self.mqtt_manager.connect,
            ("D0", 4): self.mqtt_manager.status,
            ("D0", 5): self.mqtt_manager.subscribe,
            ("D0", 6): self.mqtt_manager.publish,
            ("E0", 0): self.sd_manager.mount_card,
            ("E0", 1): self.sd_manager.unmount_card,
            ("E0", 2): self.sd_manager.list_sd_card_files,
            ("E0", 3): self.sd_manager.format_card,
            ("E0", 4): self.sd_manager.read_log_file,
            ("E0", 5): self.sd_manager.excecute_file,
            ("G0", 0): (self.config_manager.set_boot_hardware_check, False),
            ("G1", 1): (self.config_manager.set_boot_hardware_check, True),
            ("H0", 0): (self.config_manager.set_boot_animation, True),
            ("H1", 1): (self.config_manager.set_boot_animation, False),
            ("I0", 0): (self.config_manager.set_error_recovery, True),
            ("I1", 1): (self.config_manager.set_error_recovery, False),
            ("J0", 0): (self.config_manager.set_led_brightness, 0),
            ("J1", 1): (self.config_manager.set_led_brightness, 1),
            ("J2", 2): (self.config_manager.set_led_brightness, 2),
            ("J3", 3): (self.config_manager.set_led_brightness, 3),
            ("J4", 4): (self.config_manager.set_led_brightness, 4),
            ("J5", 5): (self.config_manager.set_led_brightness, 5),
            ("K0", 0): (self.config_manager.set_oled_brightness, 0),
            ("K1", 1): (self.config_manager.set_oled_brightness, 1),
            ("K2", 2): (self.config_manager.set_oled_brightness, 2),
            ("K3", 3): (self.config_manager.set_oled_brightness, 3),
            ("K4", 4): (self.config_manager.set_oled_brightness, 4),
            ("K5", 5): (self.config_manager.set_oled_brightness, 5),
            ("L0", 0): (self.config_manager.set_oled_contrast, 0),
            ("L1", 1): (self.config_manager.set_oled_contrast, 1),
            ("L2", 2): (self.config_manager.set_oled_contrast, 2),
            ("L3", 3): (self.config_manager.set_oled_contrast, 3),
            ("L4", 4): (self.config_manager.set_oled_contrast, 4),
            ("L5", 5): (self.config_manager.set_oled_contrast, 5),
            ("M0", 7): (self.config_manager.set_encoder_reverse, True),
            ("M1", 8): (self.config_manager.set_encoder_reverse, False),
            ("F0", 7): self.config_manager.save_config,
            ("F0", 8): self.config_manager.get_available_sram,
            ("F0", 9): self.config_manager.get_available_flash,
        }

    def dispatch(self, page_uid: str, cursor_position: int) -> None:
        """
        Dispatch the command to the corresponding manager.

        Parameters
        ----------
        page_uid : str, the actual page uid.
        cursor_position : int, the actual cursor position
        (given by the rotary encoder).
        """
        command_value = self.commands.get((page_uid, cursor_position))
        if command_value is None:
            print(
                f"Command not found for page_uid={page_uid}, cursor_position={cursor_position}"
            )
        elif isinstance(command_value, tuple):
            function, arg = command_value
            return function(arg)
        else:
            return command_value()
