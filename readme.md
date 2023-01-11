# mqtt_injector
An embedded device to control mqtt devices connected to a wireless network

The very frist usage of this device is simply to connect to an mqtt broker and perform
subscription and publishing on that, used to control different connected IoT devices.
Also because I'm a freakin geek fan of cyberpunk aesthetic I decided to give the project
some other functionallity in order to:
- fill up the raspberry pi pico w available GPIOs
- write a lot of disorganized python code

****HARDWARE****
- The MCU is a Raspberry Pi Pico W (RP2040).

- Pheriperals include:
  - SPI SD card reader
  - M5Stack credit card sized i2C keyboard
  - 10 segments red leds bar
  - a rotary encoder
  - a 2.7 inches i2C 128*64 blue oled display
  - a mechanical swith (kailj box navy)

- Power components(needed only for autonomous functioning) includes:
  - 18650 li-ion battery
  - 18650 battery holder
  - bms
  - receiving coil+circuit for wireless charhing of the battery (super fancy and optional)
  - a small, hard slide switch to power on and off the whole crap

****CHASSIS****
- I will soon upload the .stl 3d printable files with some printer settings
