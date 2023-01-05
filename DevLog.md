# ESP32-Edge-Impulse

The goal here is to build a temperature sensor monitor that will classify data on the ESP32, and report out over a serial connection the analysis summary of attached DS18B20 sensors

Because Edge Impulse doesn't include the sensor in their base configuration, let's knock together a quick monitor to connect to the Data Forwarder ( https://docs.edgeimpulse.com/docs/edge-impulse-cli/cli-data-forwarder ) in order to build a model.

I've started with an ESP32-WROOM that was previously running ESPHome, and had some trouble getting it up to a REPL. I tried the latest Circuit Python for the "Saola-1" https://circuitpython.org/board/espressif_saola_1_wroom/ and even tried switching to my Huzzah32 board, and getting that up with Circuit Python 8.0.0 beta 6. 
Then I remembered that Micro Python has a more generic device profile, and got 1.19.1 up to a repl. A few of the gotchas I think I was hitting are below

- fully erase flash first, every time. 
- check the intended offset for the program. Micropython says to write starting at 0x1000, CircuitPython web uploader is a bit unclear
- so I tried the esptool, with several speeds, several offsets

These instructions, modified  from https://micropython.org/download/esp32/ are what I ended up using in my case

Python3 updated to 3.11 to ensure latest pip3 
Download esptool - pip3 install esptool

```
cameron@Kitchen-iMac Downloads % esptool.py --chip esp32 -p /dev/tty.usbserial-0001 --baud 460800 write_flash -z 0x1000 esp32-20220618-v1.19.1.bin
```

The part about switching to MicroPython that's great is that I don't have to fiddle with the Adafruit sensor package or library folders, the DS18x20 driver is rolled in. That means I'm starting fresh on my main.py file.

For starters, I made a little test script to pull some temperatures in. The first_test.py file will work for making sure connections are solid, but because the MicroPython USB Serial interface drops to REPL, it won't work for the cli data forwarder, so we have to fix it up. I don't have my separate USB-TTL cable on hand, so instead of writing to a separate TTL, lets send it to the API endpoint.

For this we need to cook up a secret.py file and populate it as follows:

# secret.py
api_key = "your api key"
ssid = "your SSID"
pass = "your wifi password"

Where do we get the API key?

From your project in Edge Impulse, click the keys tab at the top, and make a new set of keys for data ingest. 

# A New Day

Back home with a USB-TTL cable at hand, a 'second serial' approach is much more favorable. I'd rather not deal with wifi and credentials and secret.py files. So onward with our approach from above.


So at this point I have an ESP-32 with screw terminals connected to 3.3v, Ground and Pin 2 for the DS18B20 leads. I've also added a 4-pin header for my UART ( 5v that I'm generally not using, Ground, Transmit and Receive ). 

Micropython has great docs, and I just hunted-and-pecked this ( https://docs.micropython.org/en/latest/esp32/quickref.html#uart-serial-bus ) example into my REPL and got... nothing on the firt try. Swapped tx/rx and got what I wanted. Its important to remember that for most devices' implementations, two devices talking need to "Transmit to the other devices' Receive" which is to say, cross Device1-Tx to Device2-Rx, D2-Tx to D1-Rx, instead of wiring Tx-Tx Rx-Rx.

# Week After Christmas

That up there is great and good for the final product, but I do think that I need for now to get data into the ingest API thingy

I'm weighing these things tenuously as these notes attest. I'll likely need to double-down on my serial com spec soon to integrate into the Sparrow part of this, but until I do, it would be nice to have a working web funnel thing for labeling samples.

I noticed in the spec for the API that I need to do some fancy signing and cryptography ( nah, bro ) but it seems I have an 'in' with the nightly builds of micropython, so here goes.

Nightly builds for the ESP32 have mip built in. mip is the micropython version of pip, which sounds awesome, so I'll throw away what I've got on the board and load a bin file labeled unstable and trust that nothing will break!

```
cameron@Kitchen-iMac Downloads % esptool.py --chip esp32 -p /dev/tty.usbserial-0001 erase_flash
esptool.py v4.4
Serial port /dev/tty.usbserial-0001
Connecting..............
Chip is ESP32-D0WDQ6 (revision v1.0)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: 24:6f:28:9c:e1:90
Uploading stub...
Running stub...
Stub running...
Erasing flash (this may take a while)...
Chip erase completed successfully in 8.7s
Hard resetting via RTS pin...
cameron@Kitchen-iMac Downloads % esptool.py --chip esp32 -p /dev/tty.usbserial-0001 --baud 460800 write_flash -z 0x1000 esp32-20221220-unstable-v1.19.1-782-g699477d12.bin
esptool.py v4.4
Serial port /dev/tty.usbserial-0001
Connecting..........
Chip is ESP32-D0WDQ6 (revision v1.0)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: 24:6f:28:9c:e1:90
Uploading stub...
Running stub...
Stub running...
Changing baud rate to 460800
Changed.
Configuring flash size...
Flash will be erased from 0x00001000 to 0x0017dfff...
Compressed 1559776 bytes to 1029813...
Wrote 1559776 bytes (1029813 compressed) at 0x00001000 in 25.1 seconds (effective 497.0 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```


With that in place, I got on wifi, ( which tripped a brownout error until I doubly connected 5v from the same USB bus power for extra juice) and banged out this 

```
>>> import mip
>>> mip.install(hmac)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'hmac' isn't defined
>>> mip.install("hmac")
Installing hmac (latest) from https://micropython.org/pi/v2 to /lib
Copying: /lib/hmac.mpy
Done
>>> 
```

which was pretty cool

# Now
I'm looking at my project keys page in Edge Impulse and there is a link the 'Data Acquisition Format' with examples. 

The Ingestion Service offers this example (https://docs.edgeimpulse.com/reference/data-ingestion/ingestion-api#data-acquisition-format)

```python
# Install requests via: `pip3 install requests`

with open('somefile.cbor', 'r') as file:
    res = requests.post(url='https://ingestion.edgeimpulse.com/api/training/data',
                        data=file,
                        headers={
                            'Content-Type': 'application/cbor',
                            'x-file-name': 'idle.01',
                            'x-label': 'idle',
                            'x-api-key': 'ei_238fae...'
                        })

    if (res.status_code == 200):
        print('Uploaded file to Edge Impulse', res.status_code, res.content)
    else:
        print('Failed to upload file to Edge Impulse', res.status_code, res.content)
```

Which should work with a little `import urequests as requets` but that `somefile.cbor` is a new mystery. Thankfully a linked document there (https://docs.edgeimpulse.com/reference/data-ingestion/data-acquisition-format) provides a little help code that I'll paste here and work up to micropython.

Oh, Time. We may have to do the NTPTime thing here instead, because time in micropython is seconds since boot, but you know what, I'm gonna see how bad they check constraints. Drop it and run it.

```python
#!/ micropython
# First, install the dependencies via:
#    $ mip.install('hmac')

#   secret.py
#   api_key = "ei_7..."
#   hmac_key = "..."
#   ssid = "..."
#   password = "..."
​
import json, time, hmac, hashlib, ubinascii, network, secret
import urequests as requests

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(secret.ssid, secret.password)
    while not wlan.isconnected():
        pass
​

HMAC_KEY = secret.hmac_key
API_KEY = secret.api_key
​mac = ubinascii.hexlify(wlan.config('mac')).decode()

# empty signature (all zeros). HS256 gives 32 byte signature, and we encode in hex, so we need 64 characters here
emptySignature = ''.join(['0'] * 64)
​
data = {
    "protected": {
        "ver": "v1",
        "alg": "HS256",
        "iat": time.time() # epoch time, seconds since 1970
    },
    "signature": emptySignature,
    "payload": {
        "device_name": mac,
        "device_type": "ESP32-DS18B20",
        "interval_ms": 10,
        "sensors": [
            { "name": "Degrees", "units": "Celsius" }
        ],
        "values": [
            [ 35 ],
            [ 35 ],
            [ 35 ],
            [ 35 ]
        ]
    }
}
​
# encode in JSON
encoded = json.dumps(data)
​
# sign message
signature = hmac.new(bytes(HMAC_KEY, 'utf-8'), msg = encoded.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()
​
# set the signature again in the message, and encode again
data['signature'] = signature
encoded = json.dumps(data)
​
# and upload the file
res = requests.post(url='https://ingestion.edgeimpulse.com/api/training/data',
                    data=encoded,
                    headers={
                        'Content-Type': 'application/json',
                        'x-file-name': 'idle01',
                        'x-api-key': API_KEY
                    })
if (res.status_code == 200):
    print('Uploaded file to Edge Impulse', res.status_code, res.content)
else:
    print('Failed to upload file to Edge Impulse', res.status_code, res.content)
```

Micropython doesn't like ~~the null string manipulation~~, balking at us with `NameError: name '​' isn't defined` 
Micropython doesn't like your assumptions, or your copy-pasta line-end characters. 

After a clean-up, `Uploaded file to Edge Impulse 200 b'idle01.3lan8ief.json'` was waiting for me on the terminal. Sweet, now lets make it actually read a sensor, and pack that in the json body. I'll leave the above for boilerplate reference, and continue editing in the EdgeImpulse.py file.

`ampy -p /dev/tty.usbserial-0001 put EdgeImpulse.py main.py  0.21s user 0.11s system 1% cpu 16.067 total`
And with that we have a one-shot data-zooka, sending temperature readings that will let us build a model!

Depending on the time sleep cycles, this can be a long running program even if not an infinte loop, so if you need to kill it with fire, control-C to break the program from USB Serial and get a REPL, then
```python
import os
os.remove("main.py")
```
and then send it again. I found that my workspace is VSCode for these md notes, git and file management, and mu for a scratchpad, using the REPL and run functions like above. Here are a few of the quick and easy 'run' functions for setting this up from scratch. Since I got worried and reloaded my board and had to start from scratch.

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

## Next Steps

# Getting Classy

I had to brush up on my pythonic class structure and inheritance, and delete a few curly braces...

then I popped this little mess in my REPL
```python
>>> class wrapper:
...     def __init__(self, net):
...         self.wlan = net
...     def connect(self, ssid, password):
...         self.wlan.active(True)
...         if not self.wlan.isconnected():
...             while not self.wlan.isconnected():
...                 pass
...
>>> import network
>>> wlan = network.WLAN(STA_IF)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'STA_IF' isn't defined
>>> wlan = network.WLAN(network.STA_IF)
>>> another = wrapper(wlan)
>>> import secret
>>> another.connect(secret.ssid, secret.password)
```

and it didn't connect because I'm in the basement, but it was a really good example of what I mean to do

I want to box up some of the work here, and get down to a saved-state, multi-sensor, portable ingest tool

I'm thinking that it will be used like this

```python
import myingestthing, secret

eat_it = myingestthing.ingest(hmac_key, api_key, ssid, password)

if eat_it.send(values):
    clear(values)
else:
    print(eat_it.error_msg)    


```