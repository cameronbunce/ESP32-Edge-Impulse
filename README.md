# ESP32-Edge-Impulse

Temperature data from DS18B20 sensor(s) attached to an ESP32 to Edge Impulse to build training and test data sets. 

Detailed notes of my fumbles in this can be found at the DevLog.md file, this has been cleaned up for clarity.

# Edge Impulse

You'll need to create an Edge Impulse account at edgeimpulse.com and clone my project https://studio.edgeimpulse.com/public/171396/latest 
With your own copy of my project, you'll get your own keys for the API. From the Project main page click on Keys at the top. Click on "Add New API Keys" on the right side. Give this a silly name, and select the role of "Ingestion" click "Create" and copy this key. Paste this key into your local copy of secret_stub.py and save it as secret.py, and go back tot he APi page for the HMAC key below the API key. This also goes in the new secret file you made, it is for signing your uploads to the API.

# Hardware setup

Begin with a generic ESP32, and a breadboard, perfboard, or a custom PCB if you're fancy. Connect the DS18B20 sensor to Vcc and Gnd, and data on ESP32 Pin 2 with a 4.7k Ohm resister pull-up. You can change this, but Pin 2 is used in the code here.

# Software Prerequisites 

Locally I updated Python3 for the latest Pip3 version and pulled down esptool.py and ampy

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
With your complete secret.py file, and your DS18B20 sensor(s) connected on Pin 2, you're ready to load EdgeImpulse.py, from the github repo directory in your terminal, 

`% ampy -p /dev/tty.usbserial-0001 put EdgeImpulse.py`

Once finished ( `ampy ... put ...` takes ~16s for me ) you can open the REPL in Mu and watch the debug messages come across. A sample is 10 readings, 10 sends apart, and the upload takes a little time as well, so a cycle is in the neighborhood of 2 minutes for the program to run. It does not loop at the moment.

# To Do

- make upload errors write the temperature values to flash
- optionally loop on interval
- figure out best way of labelling data axes ( { "name": "Temperature", "units": "Celsius" } ? )
- map out a plan for long-window sampling with lower power use