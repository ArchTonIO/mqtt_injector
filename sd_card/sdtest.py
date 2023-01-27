# from machine import Pin, SPI
# import sd_card.sdcard
# import os

# spi2 = SPI(
#     1,
#     baudrate=40000000,
#     sck=Pin(10),
#     mosi=Pin(11),
#     miso=Pin(12))
# sd = sd_card.sdcard.SDCard(spi2,Pin(13))

# vfs = os.VfsFat(sd)
# os.mount(sd,'/sd')
# print(os.listdir('/sd'))
# file = open("/sd/sample.txt","w")
# for i in range(20):
#     file.write("Sample text = %s\r\n" % i)
# file.close()

# file = open("/sd/sample.txt","a")
# file.write("Appended Sample Text at the END \n")
# file.close()

# file = open("/sd/sample.txt", "r")
# if file != 0:
#     print("Reading from SD card")
#     read_data = file.read()
#     print (read_data)
# file.close()
