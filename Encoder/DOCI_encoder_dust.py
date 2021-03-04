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

r_intensity = 70
g_intensity = 48
b_intensity = 50

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
    w=[255,200,180]
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
    Group_ID = [0,1,0]

    #Node_ID is varied according to Edge(IoT device)
    Node_ID = [0,0,0]

    prefix = Group_ID + Node_ID

    #dust
    path = '../../Dust-Sensor/dust.txt'
    with open(path) as f:
        s = f.read()
        s_split = s.split('\n')
    pmtwofive = int(float(s_split[0])*10)
    pmten = int(float(s_split[0]))
    #hour = now.hour
    #minute = now.minute
    #second = now.second

    ###environmental data
    #temperature
    temperature = int(sense.get_temperature())
    #pressure
    #only last 2 digits
    pressure = int(sense.get_pressure()) - 1000
    print("pressure", pressure)
    #humidity
    humidty = int(sense.get_humidity())

    ##data_edit-------------------------------------------------------------

    ###time
    pmtwofive_binary = myfunc.binary(pmtwofive, 8)
    pmten_binary = myfunc.binary(pmten, 10)

    ###environmental data
    temper_binary = myfunc.binary(temperature, 8)
    press_binary = myfunc.binary(pressure, 8)
    humid_binary = myfunc.binary(humidty, 8)

    ##minute_binary is splited 4bit(Spectral B) and 2bit(Spectral R)
    pmten_B = pmten_binary[0:2:1]
    pmten_G = pmten_binary[2:10:1]

    #convert edited data to RGB_array----------------------------------------------------------------------------------------------------
    ##Spectral B
    B_array = prefix + pmtwofive_binary + pmten_B
    ##Spectral G
    G_array = pmten_G + temper_binary
    ##Spectral R
    R_array = press_binary + humid_binary

    #query choice-----------------------------------------------------
    print("query:",query)

    #Queryで渡される値。Publisher側で指定している
    binary_query = [int(i) for i in query]
    print("binary_query:",binary_query)

    com_key = binary_query*2
    print("com_key:",com_key)

    # spatial encode

    #R
    R_x, R_y = myfunc.input(com_key, R_array, bit_length)
    print("R_x:",R_x)
    print("R_y:",R_y)

    #G
    G_x, G_y = myfunc.input(com_key, G_array, bit_length)
    print("G_x:",G_x)
    print("G_y:",G_y)

    #B
    B_x, B_y = myfunc.input(com_key, B_array, bit_length)
    print("B_x:",B_x)
    print("B_y:",B_y)

    # spatial encode
    R = myfunc.spatial_encode(R_x, R_y, bit_length, r_intensity, LED_array_length)
    G = myfunc.spatial_encode(G_x, G_y, bit_length, g_intensity, LED_array_length)
    B = myfunc.spatial_encode(B_x, B_y, bit_length, b_intensity, LED_array_length)

    image_array = myfunc.set_array(R, G, B , LED_array_length)
    print(image_array)

    sense.set_pixels(image_array)
    time.sleep(4)
    sense.clear()

    #これを関数にする。入力X,Y,RGBで判定する
