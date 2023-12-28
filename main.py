import sys
sys.path.insert(1, '/home/pi/iot-brewing/config')
sys.path.insert(2, '/home/pi/iot-brewing/lib')
sys.path.insert(3, '/home/pi/iot-brewing/lib/influxdb')
sys.path.insert(4, '/home/pi/iot-brewing/lib/mqtt')
sys.path.insert(5, '/home/pi/iot-brewing/lib/brewfather')
sys.path.insert(6, '/home/pi/iot-brewing/lib/grafana')

import config as cfg
import acq_tools as acq
import influxdb_tools as db
import mqtt_tools as mqtt
import brewfather_tools as bf
import grafana_tools as graf

import time

from loguru import logger
logger.add("/home/pi/iot-brewing/logs/logger.log", compression="zip" , rotation="23:59", enqueue=True)

def on_start():
    ready = False
    while 1:
        try:
            global config, measurement_name, recipe_name
            logger.debug('Opening conf file, geting recipe and creating dashboard')
            with open('/home/pi/iot-brewing/config.txt') as f:
                conf_file = f.read()
            config = json.loads(conf_file)
            start_app = config[0]["start_app"]
            if start_app:
                measurement_name = config[0]["measurement_name"]
                recipe_name = config[0]["recipe_name"]
                recipe_panel = create_recipe(recipe_name)
                dashboard = generate_dashboard(measurement_name,recipe_panel)
                send_dashboard_to_grafana(dashboard)
                logger.debug('Starting main acquisiton routine')
                main()
            else:
                logger.debug('No brewing data needed to log')
                break
        except Exception as e:
            logger.debug(e)
            time.sleep(5)
    return

def main():
    while 1:
        tiltData = acq.get_tilt_data()
        if mode == 'MQTT':
            mqtt_data = acq.format_mqtt(tiltData)
            mqtt.publish(mqtt_client,mqtt_data)
        time.sleep(cfg.updateSecs)
    return 

if __name__ == "__main__":
    mode = cfg.mode
    logger.debug('STARTING FERMENTATION MONITOR SERVICE')
    logger.debug('MODE: {}'.format(mode))
    influx_client = db.get_influxdb_client()
    mqtt_client = mqtt.connect_mqtt()
    logger.debug('Searching for last batch in Brewfather')
    batch_results,batch_name = bf.get_last_batch_results()
    logger.debug('Generating or updating last batch dashboard')
    graf.generate_dashboard(batch_results,batch_name,influx_client)
    if mode == 'TILT':
        main()
