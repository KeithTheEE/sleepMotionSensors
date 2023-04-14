# Sleep Motion Sensors
Circuit Python Code for a sleep motion sensor which uses a MPU-6050 for motion detection and runs on a QT Py ESP32-S2. 

Sensor mounts to the frame of a bed and in 40 second blocks it records motion data from the mpu6050. In 20 second blocks it transmits the data to a home server. Processing further down the line translates to motion to bed presence/absence, as well as wakefullness (via energy levels). 

## Motivation

This is a part of a larger project which is targeted at better quality sleep. 

## Build


### Electronics Parts:
- [Adafruit MPU-6050 6-DoF Accel and Gyro Sensor](https://www.adafruit.com/product/3886)
- [Adafruit QT Py ESP32-S2 WiFi Dev Board with STEMMA QT](https://www.adafruit.com/product/5325)
- [STEMMA QT QWIIC JST SH 4-Pin Cable](https://www.adafruit.com/product/4210)

### Circuit Python Libraries
These libraries can be found via the [Circuit Python Libraries Page](https://circuitpython.org/libraries)

- adafruit_mpu6050
- adafruit_bus_device
- adafruit_io
- adafruit_register
- adafruit_datetime
- adafruit_requests
- neopixel

### Custom Libraries
There are custom helper libraries I've made to simplify my smart home code or perform helpful tasks for smart home entities.

- wifi_manager (handles connection to the router and server)
- constellation_radio_ping (on startup, scans nearby networks to aid in locating position in 3D space)

