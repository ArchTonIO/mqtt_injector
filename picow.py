import network
from umqtt.simple import MQTTClient

ssid="VodafoneTPS"
password="kingoflamas99"

wlan=network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("connecting to:", ssid, "...")
while not wlan.isconnected():
    pass

print("connected to:", ssid)
print(wlan.ifconfig())

def subscribe_callback(topic, msg):
    print(topic, msg)

mqtt_client=MQTTClient("maronno1", "192.168.1.7", keepalive=60)
mqtt_client.set_callback(subscribe_callback)
mqtt_client.connect()
mqtt_client.publish("test", "test")
mqtt_client.subscribe("maronno1/test")
while True:
    mqtt_client.check_msg()

