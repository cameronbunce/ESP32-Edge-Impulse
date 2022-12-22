# Circuit Python for ESP32 Feather Huzzah from Adafruit
# mapping DS18B20 temperature sensors to USB Serial output for 
# Edge Impulse Data Forwarder

# Code largely based on Adafruit reference code
# https://learn.adafruit.com/using-ds18b20-temperature-sensor-with-circuitpython/circuitpython


import board
from adafruit_onewire.bus import OneWireBus
ow_bus = OneWireBus(board.D5)

devices = ow_bus.scan()
for device in devices:
    print("ROM = {} \tFamily = 0x{:02x}".format([hex(i) for i in device.rom], device.family_code))