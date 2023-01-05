# MicroPython for ESP32
# mapping DS18B20 temperature sensors to USB Serial output for 
# Edge Impulse Data Forwarder

# Code largely based on MicroPython Reference code
# http://docs.micropython.org/en/latest/esp32/quickref.html#onewire-driver

import time, ds18x20, onewire, urequests, ubinascii, json, secret
from machine import Pin, UART
from network import WLAN

ow = onewire.OneWire(Pin(2))
ds = ds18x20.DS18X20(ow)
uart1 = UART(1, baudrate=115200, tx=17, rx=16)
wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()
for net in nets:
    if net.ssid == secret.ssid:
        print('Network '+net.ssid+' found!')
        wlan.connect(net.ssid, auth=(net.sec, secret.password), timeout=5000)
        while not wlan.isconnected():
            machine.idle() #save power while waiting
        print('WLAN connection succeeded!')
        break

roms = ds.scan()
uart1.write("Ready reading and writing\n\r")
print(roms)
while True:
    dict={}
    time.sleep_ms(500)
    for rom in roms:
        ds.convert_temp()
        temp = ds.read_temp(rom)
        print(temp)
        uart1.write(str(temp)+"\r\n")
        #dict[ubinascii.hexlify(rom)]=temp
    #uart1.write(json.dumps(dict)+"\r\n")

