#!/ micropython
# First, install the dependencies via:
#    $ mip.install('hmac')

#   secret.py
#   api_key = "ei_7..."
#   hmac_key = "..."
#   ssid = "..."
#   password = "..."
import secret, DS18B20Reader, EdgeImpulse
from machine import deepsleep
#   Gather values for multiple sensors and write to file:
#   Read directory for contents
#   Read list of currently connected sensors
#   Write one more value to each file for each currently connected sensor
#   If 24hrs of data is stored in the file, send it to Edge Impulse
#   Sleep for 10 minutes

interval = 600000 # 10 minutes
SensorPin = 2
ReadingBatch = 145 # 24 hours of readings based on an interval of 10 minutes being 144

mysensors = DS18B20Reader.DS18B20Reader(SensorPin)
mysensors.initializeValues()
if mysensors.readCount() < ReadingBatch:
    mysensors.updateValues()
else:
    myAPI = EdgeImpulse.EIAPI(secret.api_key, secret.hmac_key, secret.ssid, secret.password)

    for sensor in mysensors.getSensors():
        if myAPI.sendValues(mysensors.getValues(sensor), interval):
            mysensors.clearValues(sensor)
        else:
            print(myAPI.getMessage())
            mysensors.updateValues()
deepsleep(interval)

