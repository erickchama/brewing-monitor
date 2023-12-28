import sys
sys.path.insert(1, '/home/pi/iot-brewing/config')

import config as cfg

from influxdb import InfluxDBClient
import time

from loguru import logger
logger.level("INFLUXDB", no=50, color="<magenta>")

def get_influxdb_client():
    host = cfg.influxdb_config['host']
    port = cfg.influxdb_config['port']
    user = cfg.influxdb_config['user']
    password = cfg.influxdb_config['password']
    db = cfg.influxdb_config['db']
    logger.log('INFLUXDB', 'Connecting to InfluxDB...')
    while 1:
        try: 
            client = InfluxDBClient(host, port, user, password, db)
            logger.log('INFLUXDB', 'Succesfully connected to DB: {}'.format(db))
            break
        except Exception as e:
            logger.log('INFLUXDB', 'Error at connecting to DB: {}'.format(e))
            time.sleep(5)
    return client

def write_data(influx_client,data):
    try:
        influx_client.write_points(data)
        logger.log('INFLUXDB','Data inserted into InfluxDB')
    except Exception as e:
        logger.log('INFLUXDB', 'Error sending data to InfluxDB: {}'.format(e))
    return