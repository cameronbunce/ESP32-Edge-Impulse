# EIAPI Class
# uploader = EIAPI(hmac, api, ssid, password)
# uplaoder.sendValues([[15], [18], [123], 10000)
# uploader.sendValues([[15, 18, 123], [16, 19, 124], [17, 20, 125] ], 10)

# one of the assumptions is that the class is handling the network connectivity
# this works in my use case but I'm open to devising an alternate constructor 
# or similar
# This depends on hmac being available ( typically as /lib/hmac.mpy on the device )
# see https://github.com/cameronbunce/ESP32-Edge-Impulse/blob/main/README.md for details 

# Public methods 
# EIAPI.sendValues(values, interval_ms) to upload one sensor's data
# EIAPI.offline() to return radio to a lower power state
# EIAPI.getMessage() to determine the failure mode, will contain all error messages
#   since last call of getMessage(), 
#   such as "SSID Not Found" 
#   or non-http200 responses from upload attempts
#   Newest will be on top
#   Messages are cleared once returned with getMessage(), 
# EIAPI.readMessage() does not clear, but returns the same as above
# EIAPI.online() is not strictly necessary, as sendValues calls it 

# To Do
# - create a generic sendValues that takes the sensor value:
#                "sensors": [
#                    { "name": "Temperature", "units": "Celsius" }
#                ],
#       as input

import network

class EIAPI:
    def __init__(self, hmac_key, api_key, ssid, password):
        import network, ubinascii
        self.wlan = network.WLAN(network.STA_IF)
        self.hmac = hmac_key
        self.api = api_key
        self.ssid = ssid
        self.password = password
        self.message = ""
        self.mac = ubinascii.hexlify(self.wlan.config('mac')).decode()
    
    def getMessage(self):
        messageOut = self.message
        self.message = ""
        return messageOut

    def readMessage(self):
        return self.message

    def __addMessage(self, update):
        # Should probably check for the stringness of update
        hold = self.message
        self.message = update+"\n\r"+hold

    def online(self):
        # get online if not online, return false if we can't find our SSID
        if self.wlan.isconnected():
            return True
        else:
            ssid_list = []
            wlan.active(True)
            rawList = self.wlan.scan()
            for one in rawList:
                ssid_list.append(one[0].decode())
            if not self.ssid in ssid_list:
                self.__addMessage("SSID Not Found")
                return False
            else:
                self.wlan.connect(self.ssid, self.password)
                while not self.wlan.is_connected():
                    pass
                return True
    
    def offline(self):
        # return the radio to a lower power state
        self.wlan.active(False)

    def __packandship(self, values, interval_ms):
        import time, json, hmac, urequests, hashlib

        # empty signature (all zeros). HS256 gives 32 byte signature, and we encode in hex, so we need 64 characters here
        emptySignature = ''.join(['0'] * 64)
        data = {
            "protected": {
                "ver": "v1",
                "alg": "HS256",
                "iat": time.time() # epoch time, seconds since poweron
            },
            "signature": emptySignature,
            "payload": {
                "device_name": self.mac,
                "device_type": "ESP32-DS18B20",
                "interval_ms": interval_ms,
                "sensors": [
                    { "name": "Temperature", "units": "Celsius" }
                ],
                "values": values
            }
        }
        encoded = json.dumps(data)
        # create signature based on blank signature field
        signature = hmac.new(bytes(self.hmac, 'utf-8'), msg = encoded.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()

        # update signature field to sign the message
        data['signature'] = signature
        post = urequests.post(url='https://ingestion.edgeimpulse.com/api/training/data',
                            data=encoded,
                            headers={
                                'Content-Type': 'application/json',
                                'x-file-name': 'idle01',
                                'x-api-key': self.api
                            })
        if (res.status_code == 200):
            return True
        else:
            self.__addMessage(res.content)
            return False
    
    def sendValues(self, values, interval_ms):
        if self.online():
            # We're online, send the values
            if self.__packandship(values, interval_ms):
                return True
            else:
                return False
        else:
            # Not online
            self.__addMessage("Not Online")
            return False