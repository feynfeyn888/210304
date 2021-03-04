# -*- coding: utf-8 -*-
import paho.mqtt.subscribe as subscribe

def topic_subscribe(encoder_IP_address, broker_IP_address):
    msg = subscribe.simple(encoder_IP_address, hostname=broker_IP_address, retained=False, msg_count=1)
    msg = subscribe.simple(host, hostname=broker_IP_address, retained=False, msg_count=1)
    topic = msg.payload

    # payloadしたmessageを返す
    return topic