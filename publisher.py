import schema_pb2
from network import WLAN
import network
import umqtt.robust as umqtt
import time
import mip
from machine import ADC


def connect(
    wifi_obj,
    ssid,
    pw,
    timeout=10
):
    wifi_obj.connect(ssid,pw)
    
    while timeout > 0:
        if wifi_obj.status() != 3:
            time.sleep(1)
            timeout-=1
        else:
            return True
    return False


def read_temp():
    global temp_sensor
    
    value = temp_sensor.read_u16()
    voltage = value * (3.3/2**16)
    temp = 27 - (voltage - 0.706)/ 0.001721
    return temp


temp_sensor = ADC(4)

#WIFI SETUP
wifi = WLAN(WLAN.IF_STA)
wifi.active(True)
ssid = "Sean's Galaxy S21 5G"
pw = "12345678"


#MQTT
HOSTNAME = '10.41.246.13'
PORT = 30000
TOPIC = 'temp/pico'


if not connect(wifi,ssid,pw):
    print("Couldnt connect To Wifi !")
    
else:
    mqtt = umqtt.MQTTClient(
            client_id = b'publish0',
            server = HOSTNAME.encode(),
            port = PORT,
            keepalive = 7000 #secs
    )
    mqtt.connect()
    while True:
        
        msg = schema_pb2.tempMessage()
        
        now = time.localtime()
        
        hour = now[3]
        minute = now[4]
        second = now[5]
        
        time_msg = schema_pb2.Time()
        time_msg.hour = hour
        time_msg.hour = minute
        time_msg.hour = second
        
        temp_msg = schema_pb2.Temp()
        temp_msg.val = int(read_temp())
        
        msg.time = time_msg
        msg.temp = temp_msg
        
        payload = msg.encode()
        
        received_msg = schema_pb2.tempMessage.decode(payload)

        print(f'payload = {payload}')
        mqtt.publish(TOPIC,payload)
        print("Sent payload")
        time.sleep(3)



