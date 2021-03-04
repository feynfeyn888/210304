from time import sleep
import paho.mqtt.subscribe as subscribe

import mylibrary-publish
import mylibrary-subscribe

##params
#符号機の数
iters = 3


#各ラズパイのIPアドレス(※固定化済み)
sub_1 = "172.16.120.130/lm75b-1/temp"
sub_2 = "172.16.120.130/lm75b-1/temp"
sub_3 = "172.16.120.130/lm75b-1/temp"
sub_4 = "172.16.120.159/lm75b-1/temp"
sub_5 = "172.16.120.159/lm75b-1/temp"

# 追加
sub_6 = "172.16.120.88/lm75b-1/temp"

#brokerのラズパイのIPアドレス
broker = "172.16.120.148"

#MacのIPアドレス(※固定化済み)
pub_address = "172.16.120.223"