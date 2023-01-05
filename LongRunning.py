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


mysensors = DS18B20Reader.DS18B20Reader(2)
mysensors.initializeValues()
if mysensors.readCount() < 145:# 24 hours of readings based on a period of 10 minutes being 144
    mysensors.updateValues()
else:
    myAPI = EdgeImpulse.EIAPI(secret.api, secret.hmac, secret.ssid, secret.password)

    for sensor in mysensors.getSensors():
        if myAPI.sendValues(mysensors.getValues(sensor)):
            mysensors.clearValues(sensor)
        else:
            print(myAPI.getMessage())
deepsleep(600000)

