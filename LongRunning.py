#!/ micropython
# First, install the dependencies via:
#    $ mip.install('hmac')

#   secret.py
#   api_key = "ei_7..."
#   hmac_key = "..."
#   ssid = "..."
#   password = "..."

#   Gather values for multiple sensors and write to file:
#   Read directory for contents
#   Read list of currently connected sensors
#   Write one more value to each file for each currently connected sensor
#   If 24hrs of data is stored in the file, send it to Edge Impulse
#   Sleep for 30 minutes


# send_values
# this function manages network connection 
# first checking to see if the intended SSID is available
# then attempting connect and send 'values' 
# Currently values is expected to be a list, but this will have to change
def send_values(values):{
    import secret, json, ubinascii, network, hashlib, hmac
    HMAC_KEY = secret.hmac_key
    API_KEY = secret.api_key
    mac = ubinascii.hexlify(wlan.config('mac')).decode()
    ssid_list = []

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    RawList = wlan.scan()
    for one in RawList:
        ssid_list.append(one[0].decode())
    
    if not secret.ssid in ssid_list:
        return False
    else:
        if not wlan.isconnected():
            wlan.connect(secret.ssid, secret.password)
            while not wlan.is_connected():
                pass
        # empty signature (all zeros). HS256 gives 32 byte signature, and we encode in hex, so we need 64 characters here
        emptySignature = ''.join(['0'] * 64)

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
                    { "name": "Temperature", "units": "Celsius" }
                ],
                "values": values
            }
        }
        # encode data to json
        encded = json.dumps(data)
        # create signature based on blank signature field
        signature = hmac.new(bytes(HMAC_KEY, 'utf-8'), msg = encoded.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()

        # update signature field to sign the message
        data['signature'] = signature
        encoded = json.dumps(data)

        # POST the file
        res = requests.post(url='https://ingestion.edgeimpulse.com/api/training/data',
                            data=encoded,
                            headers={
                                'Content-Type': 'application/json',
                                'x-file-name': 'idle01',
                                'x-api-key': API_KEY
                            })
        wlan.active(False)
        if (res.status_code == 200):
            return True
        else:
            return False

}

#   InitializeValues
#   Check folder /values for earlier readings
#   check attached sensors
def initializeValues(dallassensor)


import json, time, hmac, hashlib
import ubinascii, network, ds18x20, onewire, secret
import urequests as requests
from machine import Pin, WDT

# This is copy-pasta right now, 
# I'll organize it as the data requires

ow = onewire.OneWire(Pin(2))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
ds.convert_temp()

sensors = ""
for rom in roms:
    sensors+="{ 'name': '"+ubinascii.hexlify(rom).decode()+"', 'units': 'Celsius' },"
sensors.rstrip(',') # I didn't say it would be fancy

# determine period
readings = 0
values = []
    
while readings < 10:
    read_pass = []
    ds.convert_temp()
    for rom in roms:
        temp = ds.read_temp(rom)
        read_pass.append(temp)
    values.append(read_pass)
    time.sleep(10)
    readings+=1

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(secret.ssid, secret.password)
    while not wlan.isconnected():
        pass


HMAC_KEY = secret.hmac_key
API_KEY = secret.api_key
mac = ubinascii.hexlify(wlan.config('mac')).decode()

# empty signature (all zeros). HS256 gives 32 byte signature, and we encode in hex, so we need 64 characters here
emptySignature = ''.join(['0'] * 64)

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
            { "name": "Temperature", "units": "Celsius" }
        ],
        "values": values
    }
}


# encode in JSON
encoded = json.dumps(data)


# sign message
signature = hmac.new(bytes(HMAC_KEY, 'utf-8'), msg = encoded.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()

# set the signature again in the message, and encode again
data['signature'] = signature
encoded = json.dumps(data)

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
