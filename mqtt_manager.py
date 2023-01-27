"""
This is a class that will manage the mqtt connection
"""
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=no-method-argument
from umqtt.simple import MQTTClient


class MqttManager():
    """
    This class is used to manage the mqtt connection.
    """
    mqtt_client = None
    client_name = str()
    broker_ip = str()
    keepalive = int()
    fast_reading_topics = []
    fast_publish_topic_msg_dict = {}

    @staticmethod
    def subscribe_callback(topic, msg):
        """
        This is the callback function for the mqtt client.
        """
        print(topic, msg)

    @staticmethod
    def create_connection() -> None:
        """
        Create the connection with then specified paramenters.
        """
        MqttManager.mqtt_client = MQTTClient(
            MqttManager.client_name,
            MqttManager.broker_ip,
            keepalive=MqttManager.keepalive
        )
        MqttManager.mqtt_client.set_callback(
            MqttManager.subscribe_callback
        )

    @staticmethod
    def connect() -> None:
        """
        Connect to the broker.
        """
        MqttManager.mqtt_client.connect()

    @staticmethod
    def status() -> bool:
        """
        Return the status of the connection.
        """
        return MqttManager.mqtt_client.isconnected()

    @staticmethod
    def subscribe(topic: str) -> None:
        """
        Subscribe to a topic.
        - Args:
            - topic: the topic to subscribe to.
        """
        MqttManager.mqtt_client.subscribe(topic)

    @staticmethod
    def publish(topic: str, msg: str) -> None:
        """
        Publish a message to a topic.
        - Args:
            - topic: the topic to publish to.
            - msg: the message to publish.
        """
        MqttManager.mqtt_client.publish(topic, msg)

    @staticmethod
    def check_messages_on_broker() -> dict:
        """
        Check for messages on the broker.
        - Returns:
            - a dictionary containing the topics and the messages.
        """
        MqttManager.mqtt_client.check_msg()

    @staticmethod
    def fast_publish(key: str) -> None:
        """
        Publish a message to a topic.
        - Args:
            - key: the key of the topic and message to publish.
        """
        MqttManager.publish(
            MqttManager.fast_publish_topic_msg_dict[key][0],
            MqttManager.fast_publish_topic_msg_dict[key][1]
        )
