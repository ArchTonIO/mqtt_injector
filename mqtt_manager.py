from umqtt.simple import MQTTClient

# todo actually create this class
class mqtt_manager():
    def subscribe_callback(topic, msg):
        print(topic, msg)
    

    mqtt_client=MQTTClient("maronno1", "192.168.1.7", keepalive=60)
    mqtt_client.set_callback(subscribe_callback)
    mqtt_client.connect()
    mqtt_client.publish(topic="test", payload=  "test")
    mqtt_client.subscribe("maronno1/test")
    while True:
        mqtt_client.check_msg()