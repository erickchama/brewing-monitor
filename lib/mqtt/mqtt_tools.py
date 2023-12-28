import sys
sys.path.insert(1, '/home/pi/iot-brewing/config')

import config as cfg

import paho.mqtt.client as mqtt
import time
import json

from loguru import logger
logger.level("MQTT", no=50, color="<red>")

def connect_mqtt():
    host = cfg.mqtt_config['host']
    port = cfg.mqtt_config['port']
    try:
        logger.log('MQTT', 'Trying to connect to  MQTT broker...')
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.connect('localhost', 1883, 60)
        mqtt_client.loop_start()
    except Exception as e:
        logger.log('MQTT', 'Errot at connecting to MQTT: {}'.format(e))
    time.sleep(1)
    return mqtt_client

def on_connect(client,userdata, flags, rc):
    topics = cfg.mqtt_config['topics']
    logger.log('MQTT', "Connected to MQTT with Result Code {}".format(rc))
    # for topic in topics:
    #     client.subscribe(topic)
    #     logger.log('MQTT', "Subscribed to topic: {}".format(topic))
    return

def on_message(client, userdata, msg):
    #logger.info('Message on topic {}'.format(msg.topic))
    topic = msg.topic
    data = msg.payload
    data=json.loads(data)
    #logger.info('{}'.format(data))
    data = data
    return

def publish(client,data):
    topic = cfg.mqtt_config['publish_topic']
    client.publish(topic, json.dumps(data),0,True)
    logger.log('MQTT', 'Data sent to topic: {}'.format(topic))
    return