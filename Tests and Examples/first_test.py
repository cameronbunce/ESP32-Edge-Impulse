# MicroPython for ESP32
# mapping DS18B20 temperature sensors to USB Serial output for 
# Edge Impulse Data Forwarder

# Code largely based on MicroPython Reference code
# http://docs.micropython.org/en/latest/esp32/quickref.html#onewire-driver

import time, ds18x20, onewire
from machine import Pin
ow = onewire.OneWire(Pin(2))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
while True:
    ds.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        print(ds.read_temp(rom))
    time.sleep_ms(1000)
