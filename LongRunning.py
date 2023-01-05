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

class DS18B20Reader:
    def __init__(self, pin):
        import onewire, ds18b20
        from machine import Pin
        # setup Dallas sensor 
        self.ow = onewire.OneWire(Pin(pin))
        self.dallassensor = ds18b20.DS18B20(self.ow)
        self.Values = {}
        self.initializeValues()

    def getSensors(self):
        return Values.keys()

#   InitializeValues
#   Check values.json for earlier readings
#   Check attached sensors for new sensors
    def initializeValues(self):
        import os, json, ubinascii
        roms = self.dallassensor.scan()
        if 'values.json' not in os.listdir('/'):
            # create the data structure and store a blank copy based on the available sensors
            
            for rom in roms:
                self.Values[ubinascii.hexlify(rom).decode()] = []
            outfile = open('values.json', w)
            outfile.write(json.dumps(Values))
            outfile.close()
        else:
            # first read in the values stored
            with open('values.json') as filein:
                self.Values = json.load(filein)
            # then see if we have any new sensors
            keys = self.Values.keys()
            for rom in roms:
                strrom = ubinascii.hexlify(rom).decode()
                if strrom not in keys:
                    self.Values[strrom] = []
    
    def updateValues(self):
        # read attached sensors and update our dictionary and file
    
    def getValues(
        
    )
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
