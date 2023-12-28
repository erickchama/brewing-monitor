import sys
sys.path.insert(1, '/home/pi/iot-brewing/config')
sys.path.insert(2, '/home/pi/iot-brewing/lib/tilt')
sys.path.insert(3, '/home/pi/iot-brewing/lib/influxdb')
sys.path.insert(4, '/home/pi/iot-brewing/lib/mqtt')
sys.path.insert(5, '/home/pi/iot-brewing/lib/brewfather')
sys.path.insert(6, '/home/pi/iot-brewing/lib/grafana')

import config as cfg
import tilt_tools as tilt
import influxdb_tools as db
import mqtt_tools as mqtt
import brewfather_tools as bf
import grafana_tools as graf

import time
import setproctitle
from loguru import logger
logger.add("/home/pi/iot-brewing/logs/logger.log", compression="zip" , rotation="23:59", enqueue=True)

def main():
    logger.debug('Starting tilt data acquisition')
    while 1:
        logger.debug('Getting BrewFather last batch data')
        bf_data = bf.get_bf_data(batch_id,batch_name)
        db.write_data(influx_client,bf_data)
        if mode == 'TILT':
            logger.debug('Getting Tilt data')
            tiltData = tilt.get_tilt_data()
            influx_data = tilt.format_influxdb(tiltData,batch_name)
            mqtt_data = tilt.format_mqtt(tiltData)
            bf_data = tilt.format_bf(tiltData)
            db.write_data(influx_client,influx_data)
            mqtt.publish(mqtt_client,mqtt_data)
            bf.send_to_brewfather(bf_data)
            time.sleep(cfg.updateSecs)
    return

if __name__ == "__main__":
    setproctitle.setproctitle('brewing_monitor')
    mode = cfg.mode
    logger.debug('STARTING FERMENTATION MONITOR SERVICE')
    logger.debug('MODE: {}'.format(mode))
    influx_client = db.get_influxdb_client()
    mqtt_client = mqtt.connect_mqtt()
    batch_id,batch_name = bf.get_last_batch_id()
    logger.debug('Generating dashboard for batch: {}'.format(batch_name))
    graf.generate_dashboard(batch_name)
    main()
