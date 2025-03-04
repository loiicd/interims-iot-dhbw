from paho.mqtt import client as mqtt_client
from models.mqtt_command import MqttCommand
from models.mqtt_command import Operations

import json


class MqttSubscriber:
    """class for the mqtt connection"""
    server_ip = '192.168.1.124'
    server_port = 1883
    topic = "hochregallager/set"
    mqtt_username = 'iot'
    mqtt_password = 'iot'
    mqtt = object
    hbs = object

    def __init__(self, hbs):                # expects high_bay_storage as argument
        self.hbs = hbs                      # saves high_bay_storage as static class element
        self.mqtt = self.connect_mqtt()     # connects to the MQTT-Server
        self.subscribe(self.topic)          # subscribes to the MQTT-Topic
        self.mqtt.loop_forever()            # loops forever and waits for new messages

    def connect_mqtt(self) -> mqtt_client:
        """connects to the MQTT-Server and returns a MQTT-client"""

        def on_connect(cl, userdata, flags, rc):
            """gets called if a connection was made to a MQTT-Server"""
            if rc == 0:
                print("Connected to MQTT Broker!")
                self.subscribe(self.topic)
                print(f"Subscriped to topic: {self.topic}")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client()
        client.username_pw_set(self.mqtt_username, self.mqtt_password)
        client.on_connect = on_connect
        client.connect(self.server_ip, self.server_port)
        return client

    def subscribe(self, topic):
        """subscribes to a MQTT-Topic"""
        self.mqtt.subscribe(topic)
        self.mqtt.on_message = self.on_message    # defines the callback method for a incoming message

    # Possible MQTT-Messages in JSON-Format
    # {"operation": "DESTORE", "x": 10, "z": 5}
    # {"operation": "STORE", "x": 10, "z": 5}
    # {"operation": "REARRANGE", "x": 10, "z": 5, "x_new": 1, "z_new": 1}
    # {"operation": "STORE_RANDOM"}
    # {"operation": "DESTORE_RANDOM"}
    # {"operation": "STORE_ASCENDING"}
    # {"operation": "DESTORE_ASCENDING"}
    def on_message(self, client, userdata, msg):
        """callback method for an incoming MQTT-Message"""
        try:
            json_dict = json.loads(msg.payload)     # deserialize to a python object
            command = MqttCommand(**json_dict)
        except:
            print("Wrong MQTT message format. Format needs to be JSON-String")
            return

        if command.x != -1 and command.z != -1:
            if command.operation == Operations.STORE:
                print(f"{command.operation} to x: {command.x}, z: {command.z}")
                self.hbs.store_box(command.x, command.z)
            elif command.operation == Operations.DESTORE:
                print(f"{command.operation} to x: {command.x}, z: {command.z}")
                self.hbs.destore_box(command.x, command.z)
            elif command.operation == Operations.REARRANGE and (command.x_new != -1 or command.z_new != -1):
                print(
                    f"{command.operation} from x: {command.x}, z: {command.z} to x: {command.x_new}, z: {command.z_new}")
                self.hbs.rearrange_box(command.x, command.z, command.x_new, command.z_new)
        elif command.operation == Operations.STORE_RANDOM:
            print(f"{command.operation}")
            self.hbs.store_box_random()
        elif command.operation == Operations.DESTORE_RANDOM:
            print(f"{command.operation}")
            self.hbs.destore_box_random()
        elif command.operation == Operations.STORE_ASCENDING:
            print(f"{command.operation}")
            self.hbs.store_box_ascending()
        elif command.operation == Operations.DESTORE_ASCENDING:
            print(f"{command.operation}")
            self.hbs.destore_box_ascending()
        elif command.operation == Operations.DESTORE_OLDEST:
            print(f"{command.operation}")
            self.hbs.destore_oldest()