class DS18B20Reader:
    def __init__(self, pinnumber):
        import onewire, ds18b20
        from machine import Pin
        # setup Dallas sensor 
        self.ow = onewire.OneWire(Pin(pinnumber))
        self.dallassensor = ds18b20.DS18B20(self.ow)
        self.Values = {}
        self.initializeValues()

    def getSensors(self):
        return Values.keys()

#   initializeValues
#   Check values.json for earlier readings
#   Check attached sensors for new sensors
    def initializeValues(self):
        import os, json, ubinascii
        roms = self.dallassensor.scan()
        if 'values.json' not in os.listdir('/'):
            # create the data structure and store a blank copy based on the available sensors
            
            for rom in roms:
                self.Values[ubinascii.hexlify(rom).decode()] = []
            outfile = open('values.json', 'w')
            outfile.write(json.dumps(self.Values))
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
        import ubinascii, json
        roms = self.dallassensor.scan()
        self.dallassensor.convert_temp()
        for rom in roms:
            romstring = ubinascii.hexlify(rom).decode()
            temperature = self.dallassensor.read_temp(rom)
            self.Values[romstring].append(temperature)
        with open('values.json','w') as outfile:
            outfile.write(json.dumps(self.Values))

    
    def getValues(self, sensor):
        # return all values for a sensor
        return self.Values[sensor]
    
    def clearValues(self, sensor):
        self.Values[sensor] = []
    
    def readCount(self):
        count = 0
        for key in self.Values.keys():
            number = len(self.Values[key])
            if lnumber > count:
                count = number
        return count
