# ESP32-Edge-Impulse

The goal here is to build a temperature sensor monitor that will classify data on the ESP32, and report out over a serial connection the analysis summary of attached DS18B20 sensors

Because Edge Impulse doesn't include the sensor in their base configuration, let's knock together a quick monitor to connect to the Data Forwarder ( https://docs.edgeimpulse.com/docs/edge-impulse-cli/cli-data-forwarder ) in order to build a model.

I've started with an ESP32-WROOM that was previously running ESPHome, and had some trouble getting it up to a REPL. I tried the latest Circuit Python for the "Saola-1" https://circuitpython.org/board/espressif_saola_1_wroom/ and even tried switching to my Huzzah32 board, and getting that up with Circuit Python 8.0.0 beta 6. 
Then I remembered that Micro Python has a more generic device profile, and got 1.19.1 up to a repl. A few of the gotchas I think I was hitting are belot

- fully erase flash first, every time. 
- check the intended offset for the program. Micropython says to write starting at 0x1000, CircuitPython web uploader is a bit unclear
- so I tried the esptool, with several speeds, several offsets

These instructions, modified  from https://micropython.org/download/esp32/ are what I ended up using in my case

Python3 updated to 3.11 to ensure latest pip3 
Download esptool - pip3 install esptool

cameron@Kitchen-iMac Downloads % esptool.py --chip esp32 -p /dev/tty.usbserial-0001 --baud 460800 write_flash -z 0x1000 esp32-20220618-v1.19.1.bin

The part about switching to MicroPython that's great is that I don't have to fiddle with the Adafruit sensor package or library folders, the DS18x20 driver is rolled in. That means I'm starting fresh on my main.py file.