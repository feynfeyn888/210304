# -*- coding: utf-8 -*-
import paho.mqtt.publish as publish

def topic_publish(encoder_IP_address, message, broker_IP_address):
        #queryをブロードキャスト
        # IP__addresd, message type : string
        publish.single(encoder_IP_address, message, hostname=broker_IP_address)

