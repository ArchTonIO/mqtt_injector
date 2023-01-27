"""
This module is used as the device entry point.
All execution starts here.
"""
from hardware_manager import HwMan
from pages_manager import PagesManager

try:
    HwMan.startup_sequence()
    pages_man = PagesManager(
        HwMan.oled,
        HwMan.encoder,
        HwMan.select_button
    )
    pages_man.add_page(
        page_id=0,
        is_leaf=False,
        entries=[
            "wlan tools",
            "ble tools",
            "mqtt tools",
            "sd card tools",
            "config",
            "hardware check",
            "screen off",
            "back"
        ]
    )
    pages_man.add_page(
        page_id=1,
        is_leaf=True,
        entries=[
            "wlan scan",
            "wlan status",
            "wlan connect",
            "back"
            ]
        )
    pages_man.add_page(
        page_id=2,
        is_leaf=True,
        entries=[
            "ble status",
            "ble scan",
            "ble connect",
            "back"
        ]
    )
    pages_man.add_page(
        page_id=3,
        is_leaf=True,
        entries=[
            "fast publish",
            "fast connect",
            "mqtt set_conn.",
            "mqtt connect",
            "mqtt status",
            "mqtt subscribe",
            "mqtt publish",
            "back"
        ]
    )
    pages_man.add_page(
        page_id=4,
        is_leaf=True,
        entries=[
            "mount card",
            "umount card",
            "list files",
            "format_card",
            "read log",
            "write file",
            "excecute file",
            "back"
        ]
    )
    pages_man.add_page(
        page_id=5,
        is_leaf=False,
        entries=[
            "boot hw check",
            "boot animation",
            "error recovery",
            "led brightness",
            "oled brightnes",
            "oled contrast",
            "rverse encoder",
            "save to flash",
            "available sram",
            "availble flash",
            "back"
        ]
    )
    pages_man.loop()

except IndexError as e:
    HwMan.oled.fill(0)
    HwMan.oled.text("[FATAL ERROR]", 8, 0)
    ERROR_STR = str(e)
    COL_C = 0
    ROW_C = 30
    for i, c in enumerate(ERROR_STR):
        HwMan.oled.text(c, COL_C, ROW_C)
        COL_C += 8
        if COL_C > 120:
            COL_C = 0
            ROW_C += 10
    HwMan.oled.show()
