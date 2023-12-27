import sys
sys.path.insert(1, '/home/pi/ferm_monitor/config')
sys.path.insert(2, '/home/pi/ferm_monitor/lib')
sys.path.insert(3, '/home/pi/ferm_monitor/lib/influxdb')
sys.path.insert(4, '/home/pi/ferm_monitor/lib/mqtt')
sys.path.insert(5, '/home/pi/ferm_monitor/lib/brewfather')

import config as cfg
import acq_tools as acq
import influxdb_tools as db
import mqtt_tools as mqtt
import brewfather_tools as bf

import time


from loguru import logger
logger.add("/home/pi/ferm_monitor/logs/logger.log", compression="zip" , rotation="23:59", enqueue=True)

def send_dashboard_to_grafana(dashboard):
    try:
        headers =  {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Authorization": "Bearer eyJrIjoiM00yUVpibkJINkpoNmRtemFyaktvTTRwZEtlaWpveE8iLCJuIjoicHl0aG9uIiwiaWQiOjF9"
                   }
        server= "http://localhost:3000"
        url = server + "/api/dashboards/db"
        payload = {"dashboard": dashboard}
        p = requests.post(url, headers=headers, json=payload)
        logger.debug(p)
    except Excetion as e:
        logger.debug(e)
    return

def generate_dashboard(measurement_name,recipe_panel):
    with open('/home/pi/tilt_IoT_v2/base_dashboard.json','r') as f:
        dashboard = json.load(f)
    rep_query = """SELECT last(\"init_ph\"), last(\"final_ph\"), last(\"original_g\"), last(\"t_gravity\"), last(\"t_volume\"), last(\"a_volume\"), last(\"t_eff\"), last(\"a_eff\") FROM \"{}\"""".format(measurement_name)
    for panel in dashboard["panels"]:
        if panel['title'] == 'Recipe':
            panel['options']['content'] = recipe_panel
        if 'fieldConfig' in panel.keys():
            if 'overrides' in panel['fieldConfig']:
                if panel['fieldConfig']['overrides'] != []:
                    if 'Time' in panel['fieldConfig']['overrides'][0]['matcher']['options']:
                        pass
                    else:
                        panel['fieldConfig']['overrides'][0]['matcher']['options'] = measurement_name + '.last'
        if 'targets' in panel.keys():
            if 'measurement' in panel["targets"][0]:
                panel["targets"][0]["measurement"] = measurement_name
    for target in dashboard["panels"][0]["targets"]:
        if 'query' in target.keys():
            target["query"] = rep_query
        target["measurement"] = measurement_name
    dashboard["title"] = measurement_name
    return dashboard

def on_start():
    ready = False
    while 1:
        try:
            global config, measurement_name, recipe_name
            logger.debug('Opening conf file, geting recipe and creating dashboard')
            with open('/home/pi/ferm_monitor/config.txt') as f:
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
    mode = cfg.mode
    while 1:
        tiltData = acq.get_tilt_data()
        if mode == 'MQTT':
            mqtt_data = acq.format_mqtt(tiltData)
            mqtt.publish(mqtt_client,mqtt_data)
        time.sleep(cfg.updateSecs)
    return 

if __name__ == "__main__":
    logger.debug('STARTING FERMENTATION MONITOR SERVICE')
    influx_client = db.get_influxdb_client()
    mqtt_client = mqtt.connect_mqtt()
    batch_results = bf.get_last_batch_results()
    db.write_data(influx_client,batch_results)
    #main()
