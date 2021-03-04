# -*- coding: utf-8 -*-

from time import sleep

import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

from mymodule import mylibrary_publish
from mymodule import mylibrary_subscribe

# broker IP address
broker = "172.16.120.148"

# Mac IP address
pub_address = "172.16.120.185"
sub_address = "172.16.120.185/lm75b-1/temp"
# sub_address = "172.16.120.185/lm75b-1/temp"
# publish
msg = "19"
mylibrary_publish.topic_publish(sub_address, msg, broker)
print("publish and wait 10 second")

sleep(1)

# subscribe
print("subscribe")
msg = mylibrary_subscribe.topic_subscribe(sub_address, broker)
print("msg:", msg)