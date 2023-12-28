import blescan
import sys
import time
import bluetooth._bluetooth as bluez
import logging
from influxdb import InfluxDBClient
import json
import requests
from brewfather_integration import *

def setup_logger(name, log_file, level=logging.DEBUG):
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def get_data():
    got_data = False
    tiltSG=tiltTemp=tiltColour=tiltOG=tiltBeer=tiltAbv=tiltAA=phI=phF=tgravity=t_volume=a_volume=t_eff=a_eff = None
    try:
        sock = bluez.hci_open_dev(dev_id)
    except:
        logger.debug("Error accessing bluetooth device...")
        sys.exit(1)
    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)
    returnedList = blescan.parse_events(sock, 10)
    for beacon in returnedList:
        output = beacon.split(',') 
        if output[1] in devices.keys():
            got_data = True
            tempc = round(((float(output[2])/10) - 32) * 0.5556,2)
            tiltSG = float(output[3])/10000
            tiltTemp = tempc
            tiltColour = devices[output[1]]
            for dev in config:
                    if tiltColour in dev.values():
                        tiltOG = dev["original_gravity"]
                        tiltBeer = dev["beer_name"]
                        tiltAbv = round((tiltOG - tiltSG) * 131.25,2)
                        tiltAA = round((tiltAbv/tiltOG) * 20, 2)
                        phI = dev["init_ph"]
                        phF = dev["final_ph"]
                        tgravity = dev["target_gravity"]
                        t_volume = dev["target_volume"]
                        a_volume = dev["actual_volume"]
                        t_eff = dev["target_efficiency"]
                        a_eff = dev["actual_efficiency"]
    if not got_data:
        logger.debug('No Tilt was found on returnedList')
    blescan.hci_disable_le_scan(sock)
    return tiltSG, tiltTemp, tiltColour, tiltOG, tiltBeer, tiltAbv, tiltAA,phI,phF,tgravity,t_volume,a_volume,t_eff,a_eff,got_data

def build_jsons(tiltSG,tiltTemp,tiltColour,tiltOG,tiltBeer,tiltAbv,tiltAA,phI,phF,tgravity,t_volume,a_volume,t_eff,a_eff,bf_counter):
    to_send = [{
              "measurement": measurement_name,
              "tags": {
                      "name": tiltBeer,
                      "color": tiltColour
                      },
              "fields": {
                        "temp": tiltTemp,
                        "gravity": tiltSG, #- calibration,
                        "alcohol_by_volume": tiltAbv,
                        "apparent_attenuation": tiltAA,
                        "beername": tiltBeer,
                        "init_ph": phI,
                        "final_ph": phF,
                        "original_g": tiltOG,
                        "t_gravity": tgravity,
                        "t_volume": t_volume,
                        "a_volume":a_volume,
                        "t_eff":t_eff,
                        "a_eff":a_eff
                        }
              }]
    if bf_counter == 3:
        to_send_bf = {'name':'green_tilt',
                      'temp':tiltTemp,
                      'temp_unit':'C',
                      'gravity':tiltSG,
                      'gravity_unit':'G'}
    else:
        to_send_bf = None
    return to_send,to_send_bf

def send_to_brewfather(to_send_bf):
    url = 'http://log.brewfather.net/stream?id=juqWHHX8re7Sgu'
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(to_send_bf))
        logger.debug(response)
        logger.debug("Tilt reading posted successfully in Brewfather")
    except Exception as e:
        logger.debug(e)
    return

def main():
    bf_counter = 0
    while 1:
        tiltSG, tiltTemp, tiltColour, tiltOG, tiltBeer, tiltAbv, tiltAA,phI,phF, tgravity,t_volume,a_volume,t_eff,a_eff,got_data = get_data()
        if got_data:
            bf_counter += 1
            logger.debug('Data acquired')
            to_send,to_send_bf = build_jsons(tiltSG, tiltTemp, tiltColour, tiltOG, tiltBeer, tiltAbv, tiltAA, phI, phF, tgravity,t_volume,a_volume,t_eff,a_eff,bf_counter)
            logger.debug('Json created and ready to send')
            client.write_points(to_send)
            logger.debug('Data sent to InfluxDB')
            if to_send_bf is not None:
                bf_counter = 0
                logger.debug('Sending data to Brewfather custom stream')
                send_to_brewfather(to_send_bf)
        else:
            logger.debug('Retrying to get data...')
        time.sleep(updateSecs)

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
            with open('/home/pi/tilt_IoT_v2/config.txt') as f:
                conf_file = f.read()
            config = json.loads(conf_file)
            start_app = config[0]["start_app"]
            if start_app == 'True':
                measurement_name = config[0]["measurement_name"]
                recipe_name = config[0]["recipe_name"]
                recipe_panel = create_recipe(recipe_name)
                print(recipe_panel)
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

if __name__ == "__main__":
    devices =   {
                'a495bb10c5b14b44b5121370f02d74de':'red',
                'a495bb20c5b14b44b5121370f02d74de':'green',
                'a495bb30c5b14b44b5121370f02d74de':'black',
                'a495bb40c5b14b44b5121370f02d74de':'purple',
                'a495bb50c5b14b44b5121370f02d74de':'orange',
                'a495bb60c5b14b44b5121370f02d74de':'blue',
                'a495bb70c5b14b44b5121370f02d74de':'yellow',
                'a495bb80c5b14b44b5121370f02d74de':'pink'
                }
    dev_id = 0
    calibration = 0.003
    updateSecs = 300
    formatter = logging.Formatter('%(asctime)s %(message)s')
    logger = setup_logger('TILT_LOGGER', '/home/pi/tilt_IoT_v2/logger.log')
    client = InfluxDBClient('localhost', 8086, 'pi', 'veridisquo', 'tilt')
    on_start()
