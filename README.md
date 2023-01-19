# ESP32-Edge-Impulse

Temperature data from DS18B20 sensor(s) attached to an ESP32 to Edge Impulse to build training and test data sets. 

Detailed notes of my fumbles in this can be found at the DevLog.md file, this has been cleaned up for clarity.

# Edge Impulse

You'll need to create an Edge Impulse account at edgeimpulse.com and clone my project https://studio.edgeimpulse.com/public/171396/latest 
With your own copy of my project, you'll get your own keys for the API. From the Project main page click on Keys at the top. Click on "Add New API Keys" on the right side. Give this a silly name, and select the role of "Ingestion" click "Create" and copy this key. Paste this key into your local copy of secret_stub.py and save it as secret.py, and go back to the APi page for the HMAC key below the API key. This also goes in the new secret file you made, it is for signing your uploads to the API.

# Hardware setup

Begin with a generic ESP32, and a breadboard, perfboard, or a custom PCB if you're fancy. Connect the DS18B20 sensor to Vcc and Gnd, and data on ESP32 Pin 2 with a 4.7k Ohm resister pull-up. You can change this, but Pin 2 is used in the code here.

# Software Prerequisites 

I updated Python3 for the latest Pip3 version and pulled down esptool.py and ampy

`pip3 install esptool`
`pip3 install adafruit-ampy`

I have VSCode and Mu installed for different uses. VSCode integrates well with git and handles note-taking and version control. Mu is good for REPL and serial monitoring, and ampy is for verifying assumptions. 

I'm using a nightly build of MicroPython from https://micropython.org/download/esp32/ because it has a built in package manager, which we will use. The file I use in this is esp32-20221220-unstable-v1.19.1-782-g699477d12.bin but a newer one may be available. 

We begin by clearing the board, my Mac calls my device tty.usbserial-0001, but yours may vary. Check this by the terminal with `ls /dev | grep tty` before and after connecting your board.

`% esptool.py --chip esp32 -p /dev/tty.usbserial-0001 erase_flash`

Then we write the firmware.

`% esptool.py --chip esp32 -p /dev/tty.usbserial-0001 --baud 460800 write_flash -z 0x1000 esp32-20221220-unstable-v1.19.1-782-g699477d12.bin`

Now we need to get online. You could bang all the commands into the Mu REPL window, and that's a good way to learn, but there's one thing we can do here to make the future easier for us. If you started filling in your secret.py file above, you're going to fill the rest in now. Otherwise, right now we need the ssid and password part in a file called secret.py and loaded on the ESP32. So make your secret.py file and fill in at least:

```python
ssid = "MySSID"
password = "Sup3r5ecr3tP4ssword"
```

And use ampy to get that file on the board

`% ampy -p /dev/tty.usbserial-0001 put /path/to/secret.py`

Now in Mu you can paste the following in a tab, open the REPL, and press run. Your ESP32 will use the SSID and Password stored int he secret file to connect to your home network, it will then use that connection to pull down the HMAC library using mip, which is the micropython version of pip.

```python
import network, mip, secret
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(secret.ssid, secret.password)
    while not wlan.isconnected():
        pass

mip.install('hmac')
```
With your complete secret.py file, and your DS18B20 sensor(s) connected on Pin 2, you're ready to load the example, from the repo's "Tests and Examples"  directory in your terminal.

If you used a different pin, you can SensorPin to the pin you used. Debug messages will print to the serial interface, so you can watch for any trouble uploading that way. With that set, we'll put it on the board, but rename it main.py for the board to run.

```python
import json, time, hmac, hashlib
import ubinascii, network, ds18x20, onewire, secret
import urequests as requests
from machine import Pin, WDT

debug = True
SensorPin = 2 # a DS18B20 attached on pin 2
```


`% ampy -p /dev/tty.usbserial-0001 put EdgeImpluse_DS18B20_example.py main.py`

Once finished ( `ampy ... put ...` takes ~16s for me ) you can open the REPL in Mu and watch the debug messages come across. A sample is 10 readings, 10 seconnds apart, and the upload takes a little time as well, so a cycle is in the neighborhood of 2 minutes for the program to run. It does not loop at the moment.

If your upload doesn't throw errors, and the data shows up in Edge Impulse, then you're ready to dig in with the main directory of the repo.

LongRunning.py uses deep sleep on the ESP32 to save battery and take readings spaced out over a whole day if needed. Let's look at where to find the controls for those periods.

```python
interval = 600000 # 10 minutes
SensorPin = 2
ReadingBatch = 145 # 24 hours of readings with interval = 10 minutes being 144
```

The SensorPin is just like before, but there is no debug? We write any important messages to the flash on the ESP32. When we put the processor in Deep Sleep, we have to make sure any information we need is in flash, so the sensor readings and the messages ( "SSID Not Found" or any non-200 response from the API ) are written to files before we go to sleep. They are craftily called message.txt and values.json and should allow us to upload data even if we run out of battery in the field or pull power.

`% ampy -p /dev/tty.usbserial-0001 put DS18B20Reader.py`
`% ampy -p /dev/tty.usbserial-0001 put EdgeImpulse.py`
`ampy -p /dev/tty.usbserial-0001 put LongRunning.py main.py`

A word of note: ESP32 devices in deep sleep are really unresponsive.

If you need to interrupt the program to recover it you will want to keep it from returning to main.py, so put the following code in Mu or Thonny and restart the device. Press Control-C to break out to the REPL, and then run this:

```python
import os
os.remove("main.py")
```

You can then check the messages and see what's happening and update as necessary. Other troubleshooting and my whole process to this point is available in the DevLog.md file.

You now have an automatic data feeding machine to build better ML models. Use your powers for awesome.

# To Do

- make upload errors write the temperature values to flash
- optionally loop on interval
- figure out best way of labelling data axes ( { "name": "Temperature", "units": "Celsius" } ? )
- map out a plan for long-window sampling with lower power use