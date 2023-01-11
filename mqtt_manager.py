"""
This is a class that will manage the mqtt connection
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
from umqtt.simple import MQTTClient


class MqttManager():
    """
    This class is used to manage the mqtt connection.
    """
    def subscribe_callback(self, topic, msg):
        """
        This is the callback function for the mqtt client.
        """
        print(topic, msg)
    mqtt_client = MQTTClient("maronno1", "192.168.1.7", keepalive=60)
    mqtt_client.set_callback(subscribe_callback)
    mqtt_client.connect()
    mqtt_client.publish(topic="test", payload="test")
    mqtt_client.subscribe("maronno1/test")
    while True:
        mqtt_client.check_msg()
