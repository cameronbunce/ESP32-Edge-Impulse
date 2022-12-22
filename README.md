# ESP32-Edge-Impulse

The goal here is to build a temperature sensor monitor that will classify data on the ESP32, and report out over a serial connection the analysis summary of attached DS18B20 sensors

Because Edge Impulse doesn't include the sensor in their base configuration, let's knock together a quick monitor to connect to the Data Forwarder ( https://docs.edgeimpulse.com/docs/edge-impulse-cli/cli-data-forwarder ) in order to build a model.

I've started with an Adafruit Huzzah Feather ESP32 ( the old one, because it was laying around ) and updated it to Circuit Python 8.0.0 beta 6

