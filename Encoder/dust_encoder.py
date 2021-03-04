#coding: utf-8

"""
###Code Assignment
---Spectral B channel---
Group ID (3bit) [g2g1g0]
Node ID (3bit) [i2i1i0]
Time_1 (10bit(6bit,4bit)) [h5h4h3h2h1h0][m5m4m3m2]

---Spectral G channel---
Time_2 (8bit) [m1m0][s5s4s3s2s1s0]
Temperature (8bit) [a5a4a3a2a1a0]

---Spectra R channel---
Atmospheric Pressure (8bit) [b5b4b3b2b1b0]
Humidity (8bit) [c5c4c3c2c1c0]

###Data Format and Prefixed Values
Encryption Common Key:  10101101
Group ID:  010
Node ID:    000, 001, 010, 011, 100
Time: (0〜23 : 0〜59 : 0〜59)   [h5h4h3h2h1h0][m5m4m3m2m1m0][s5s4s3s2s1s0]
Temperature: (0〜100) [deg]    [a5a4a3a2a1a0]
Atmospheric pressure: (0〜100)[%][hPa]     [b5b4b3b2b1b0]
Humidity: (0〜100)[%]  [c5c4c3c2c1c0]
"""


import cv2
import time
from time import sleep
from datetime import datetime
import numpy as np
import paho.mqtt.subscribe as subscribe
from sense_hat import SenseHat

# Module for Dust Sensor
import serial
import time

#myfunction
import Encoder_myfunction

#Myfunc class
myfunc = Encoder_myfunction.MyClass()

#Sensehat class
sense = SenseHat()

#Params---------------------------------------------------------------

# MQTT Broker
MQTT_HOST = "172.16.120.148"    # brokerのアドレス
MQTT_PORT = 1883                # brokerのport
MQTT_KEEP_ALIVE = 60            # keep alive

# query bit length
bit_length = 16

# LED光強度
Dust_intensity = 200

# LED array size
LED_array_length = 64

DOC_loop = True
subscribe_loop = True
while DOC_loop:
    while subscribe_loop:
        print("start")
        msg = subscribe.simple("Topic", hostname=MQTT_HOST)
        print("msg.payload:", msg.payload)

        # if msg.payload include "query", DOC starts
        if 'query' in (msg.payload).decode():
            query = (msg.payload).decode()[-8:]
            # key = msg.payload[-8:] 後ろから8文字=Queryの長さの分切り出す
            print("query:", query)
            break

    # 撮影のため全点灯・全消灯
    print("DOC start")

    #------------------------------符号器検出(背景差分)
    e=[0,0,0]
    w=[120,120,120]
    z3 = [e]*64
    #z4 = [w]*64
    z4 = [
        w,w,w,w,w,w,w,w,
        w,w,w,e,e,w,w,w,
        w,w,e,w,e,w,w,w,
        w,w,w,w,e,w,w,w,
        w,w,w,w,e,w,w,w,
        w,w,w,w,e,w,w,w,
        w,w,e,e,e,e,w,w,
        w,w,w,w,w,w,w,w,
        ]

    #1
    #点灯
    sense.set_pixels(z4)
    time.sleep(5)
    sense.clear()
    #消灯
    time.sleep(5)

    #Params to be Encoded------------------------------------------------------------------------------------------------

    #prefix=01
    ##This time, Group_ID is static.
    Node_ID = [0,1]

    #Node_ID is varied according to Edge(IoT device)
    Sensor_Info_ID = [0,0]

    prefix = Node_ID + Sensor_Info_ID
    print("prefix:", prefix)
    print("prefix type:", type(prefix))
    print("prefix[0] type:", type(prefix[0]))

    ###environmental data
    # serial takes these two parameters: serial device and baudrate(変調回数)
    ser = serial.Serial('/dev/ttyUSB0', 9600)


    data = []
    for index in range(0, 10):
        datum = ser.read()
        # print(datum)
        data.append(datum)

    pmtwofive = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    pmten = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10

    print("pmtwofive", pmtwofive)
    print("pmten", pmten)

    pmtwofive = int(pmtwofive)
    pmten = int(pmten)

    ###binary
    pmtwofive_binary = myfunc.binary(pmtwofive, 4)
    pmten_binary = myfunc.binary(pmten, 8)

    with open("dustinfo.txt", "w") as f:
        f.write(str([pmtwofive, pmten]))

    print("pmtwofive binary", pmtwofive_binary)
    print("pmten binary", pmten_binary)

    #convert edited data to RGB_array----------------------------------------------------------------------------------------------------
    ##Spectral B
    #pmtwofive_binary.extend(pmten_binary)
    Dust_array = prefix + pmtwofive_binary + pmten_binary
    print("Dust_array:", Dust_array)

    #query choice-----------------------------------------------------
    print("query:",query)

    #Queryで渡される値。Publisher側で指定している
    binary_query = [int(i) for i in query]
    print("binary_query:",binary_query)

    com_key = binary_query*2
    print("com_key:",com_key)

    # encode
    Dust_x, Dust_y = myfunc.input(com_key, Dust_array, bit_length)
    print("Dust_x:",Dust_x)
    print("Dust_y:",Dust_y)

    # spatial encode
    Dust_DOC = myfunc.spatial_encode(Dust_x, Dust_y, bit_length, Dust_intensity, LED_array_length)
    image_array = myfunc.set_array(Dust_DOC, Dust_DOC, Dust_DOC , LED_array_length)
    print(image_array)

    sense.set_pixels(image_array)
    time.sleep(5)
    sense.clear()

    #これを関数にする。入力X,Y,RGBで判定する
