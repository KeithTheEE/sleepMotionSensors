import time
import board
import busio
import adafruit_mpu6050
import microcontroller


import rtc
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import wifi
import socketpool
import neopixel
import adafruit_requests 
from adafruit_requests import OutOfRetries
import json
import gc
import ipaddress
import ssl


import wifi_manager
import constellation_radio_ping

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3)
pixels.direction = digitalio.Direction.OUTPUT

pixels[0] = (180, 0, 255)
pixels.show()


def get_meta_data():
    

    return {}


# Needed for qtpy
i2c = busio.I2C(sda=board.SDA1, scl=board.SCL1)
mpu = adafruit_mpu6050.MPU6050(i2c)




def set_time(server_time, offset, query_elapse):
    r = rtc.RTC()
    r.datetime = time.struct_time(server_time)
    return r



# initalize Network
NETWORK_QUIETMODE = False # Will ignore all network communication while Set to True
my_network = wifi_manager.Current_Web_Status(NETWORK_QUIETMODE)
my_network.connect_with_mywifi()
my_network.start_sessions_pool()


# Set internal Clock
time_request_made = time.monotonic_ns()/10**9
cur_time = my_network.get_json("http://192.168.1.147:5000/api/current_time_since_epoch")
#print(cur_time)
request_elapse = time.monotonic_ns()/10**9 - time_request_made
print(cur_time)
# If you can reach network, set time
if not isinstance(cur_time, type(None)):
    print("GOING TO SET TIME")
    # Only set time if the server query returned something
    time_tuple = cur_time['utc_time_tuple']
    r = set_time(time_tuple, time_request_made, request_elapse)
    # Setting up time based checks
    last_hour = r.datetime.tm_hour
    hours_since_reset = 0
    print(r.datetime.tm_hour)
    rtc_set = True
else: 
    # Setting up time based checks
    print("Failed to set time")
    r = rtc.RTC()
    last_hour = r.datetime.tm_hour
    hours_since_reset = 0
    print(r.datetime.tm_hour)
    rtc_set = False


myip = str(my_network._my_ip)[-3:]
if myip == '104':
    pixels[0] = (31, 119, 180)
if myip == '118':
    pixels[0] = (255, 127, 14)
if myip == '203':
    pixels[0] = (44, 160, 44)
if myip == '177': # this is the 'extra' sensor 
    pixels[0] = (200, 10, 100)
pixels.show()
time.sleep(5)

pixels[0] = (0,0,0)
pixels.show()

x = []
z = []
'''52
Seconds: 59  Packet Size Remaining: 16004
Fake Sending Data
16004 139280

Memory Limit:

Program failed at 16004 packets in x where a packet was comprised of:
        start_time = time.monotonic_ns() / 10**9
        y = {}
        #y['timestamp'] = time.mktime(rtc.RTC().datetime)
        y['time_monotonic_ns'] = start_time
        y['Acceleration'] = mpu.acceleration
        y['Gyro'] = mpu.gyro
        x.append(y)

it had 139280 bytes remaining prior to another batch of updates

Setting soft limit to 8000 and trimming when hit at 5000
to give sufficent space as the program scope creep increases

'''
packet_size = 15
max_history_limit = 8000
history_trim_to_size = 5000
time_delay = 0.2

post_sensor_webpage = "http://192.168.1.147:5000/api/sleep_monitor"

sleep_times = []

while True:
    if len(x) > max_history_limit:
        # Trim back the data to prevent memory error
        x = x[-history_trim_to_size:]
    if r.datetime[5] > 40:
        # Currently in Non-Sampling section of code
        '''
        What are all of the things I need to manage in this 20 span
        - update rtc if needed
        - Add index to to last minutes samples for simpler post processing
        - get the temp of the board add to first packet of the minute
        - DEBUGGING toggle led if sleep time was ever less than 0 AND datetime.seconds < 55
        - Add a flag to the first packet if sleep time was ever less than 0
        '''
        # If index values haven't been added to x, add them

        # If the above, get and add the temp to the 0th index as well

        # if len(sleep_times) > 0:
        #     print(sleep_times)
        sleep_times = []
        start_time = time.monotonic_ns() / 10**9



        # #----------Internal Clock Reset----------# #
        # Check if we need to resync the time
        if last_hour != r.datetime.tm_hour:
            hours_since_reset += 1
        if (hours_since_reset > 16 and r.datetime.tm_hour >= 22) or not rtc_set: # UTC 
            print("Attempting to ReSync Clock")
            time_request_made = time.monotonic_ns()/10**9
            cur_time = my_network.get_json("http://192.168.1.147:5000/api/current_time_since_epoch")
            #print(cur_time)
            request_elapse = time.monotonic_ns()/10**9 - time_request_made
            #print(cur_time)
            # If you can reach network, set time
            if not isinstance(cur_time, type(None)):
                #print("GOING TO SET TIME")
                # Only set time if the server query returned something
                time_tuple = cur_time['utc_time_tuple']
                r = set_time(time_tuple, time_request_made, request_elapse)
                hours_since_reset = 0
                rtc_set = True


        # #----------Check if Header is Built for latest Minute----------# #
        '''
        check if minute has been built/parsed with a header
        if not
            - get minute this minute refers to
            - get micro temp
            - get acc temp
            - get sample counts
            - reformat  
        '''





        # #----------Send off Data Packets----------# #
        if len(x)>0:
            print("Seconds:", r.datetime[5], " Packet Size Remaining:",len(x))
            #print(x[:10])
            temp_packet = {'ip':str(my_network._my_ip), 'packet':x[:packet_size]}
            
            packet = json.dumps(temp_packet)
            success = my_network.post_sensor_packet(packet, post_sensor_webpage)
            if success:
                print("Sent")
                if len(x)>packet_size:
                    x = x[packet_size:]
                else: 
                    x = []
                pixels[0] = (0, 0, 0)
            else:
                pixels[0] = (50, 0, 0)
                #time.sleep(.1)
            pixels.show()

            # Post the data

        # Sleep between no and 0.1 second adjusted for the time of the sensor reads
        sleep_time = min(1, max(0, 1-((time.monotonic_ns() / 10**9)-start_time)))
        if len(x) > 0:
            sleep_time = 0
        #print("SLeeping", sleep_time)
        if sleep_time > 0:
            time.sleep(sleep_time)  
    else:
        # #----------Record Sensor Data----------# #
        start_time = time.monotonic_ns() / 10**9
        y = {}
        y['timestamp'] = time.mktime(rtc.RTC().datetime)
        y['time_monotonic_ns'] = start_time
        y['Acceleration'] = mpu.acceleration
        y['Gyro'] = mpu.gyro
        #y['temp_c'] = mpu.temperature
        x.append(y)
        # Sleep between no and 0.2 second adjusted for the time of the sensor reads
        sleep_time = min(time_delay, max(0, time_delay-((time.monotonic_ns() / 10**9)-start_time)))
        #print("SLeeping", sleep_time)
        sleep_times.append(sleep_time)
        if sleep_time > 0:
            time.sleep(sleep_time)  
        # else:
        #     print("Warning", sleep_time)