#!/ micropython
# First, install the dependencies via:
#    $ mip.install('hmac')

#   secret.py
#   api_key = "ei_7..."
#   hmac_key = "..."
#   ssid = "..."
#   password = "..."

import json, time, hmac, hashlib
import ubinascii, network, ds18x20, onewire, secret
import urequests as requests
from machine import Pin, WDT

# This is copy-pasta right now, 
# I'll organize it as the data requires
debug = True

if debug:
    wdt = WDT(timeout=10000)
    print("Watchdog Timer started with 10s timeout")

ow = onewire.OneWire(Pin(2))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
ds.convert_temp()

if debug:
    print("DS18B20 scan complete")
    wdt.feed()

sensors = ""
for rom in roms:
    sensors+='{ "name": "'+ubinascii.hexlify(rom).decode()+'", "units": "Celsius" },'
sensors.rstrip(',') # I didn't say it would be fancy

if debug:
    wdt.feed()
    print("Taking temperature readings")

# determine period
readings = 10
values = []

while readings > 0:
    # ds.convert_temp()
    time.sleep(750)
    read_pass = []
    for rom in roms:
        read_pass.append(ds.read_temp(rom))
    readings-=1
    values.append(read_pass)
    if debug:
        print(read_pass)
        wdt.feed() # currently breaking here, not getting to this feed point even with the read_temp() ignored. 
    time.sleep(100)

if debug:
    print("Wifi setup")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(secret.ssid, secret.password)
    while not wlan.isconnected():
        pass

if debug:
    print("connected")
    wdt.feed()

HMAC_KEY = secret.hmac_key
API_KEY = secret.api_key
mac = ubinascii.hexlify(wlan.config('mac')).decode()

# empty signature (all zeros). HS256 gives 32 byte signature, and we encode in hex, so we need 64 characters here
emptySignature = ''.join(['0'] * 64)

if debug:
    print("Packing Data")

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
            sensors
        ],
        "values": values
    }
}
if debug:
    print(data)
    wdt.feed()

# encode in JSON
encoded = json.dumps(data)

if debug:
    print("Signing")

# sign message
signature = hmac.new(bytes(HMAC_KEY, 'utf-8'), msg = encoded.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()

# set the signature again in the message, and encode again
data['signature'] = signature
encoded = json.dumps(data)

# and upload the file
if debug:
    print("Sending")
    wdt.feed()

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
