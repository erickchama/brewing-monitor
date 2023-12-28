import requests
import json

import sys
sys.path.insert(1, '/home/pi/iot-brewing/lib/influxdb')

import influxdb_tools as db

from loguru import logger
logger.level("GRAFANA", no=50, color="<green>")

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
        logger.log('GRAFANA',p)
    except Exception as e:
        logger.log('GRAFANA','ERROR:'.format(e))
    return

# def generate_dashboard(measurement_name,recipe_panel):
#     with open('/home/pi/iot-brewing/lib/grafana/base_dashboard.json','r') as f:
#         dashboard = json.load(f)
#     rep_query = """SELECT last(\"init_ph\"), last(\"final_ph\"), last(\"original_g\"), last(\"t_gravity\"), last(\"t_volume\"), last(\"a_volume\"), last(\"t_eff\"), last(\"a_eff\") FROM \"{}\"""".format(measurement_name)
#     for panel in dashboard["panels"]:
#         if panel['title'] == 'Recipe':
#             panel['options']['content'] = recipe_panel
#         if 'fieldConfig' in panel.keys():
#             if 'overrides' in panel['fieldConfig']:
#                 if panel['fieldConfig']['overrides'] != []:
#                     if 'Time' in panel['fieldConfig']['overrides'][0]['matcher']['options']:
#                         pass
#                     else:
#                         panel['fieldConfig']['overrides'][0]['matcher']['options'] = measurement_name + '.last'
#         if 'targets' in panel.keys():
#             if 'measurement' in panel["targets"][0]:
#                 panel["targets"][0]["measurement"] = measurement_name
#     for target in dashboard["panels"][0]["targets"]:
#         if 'query' in target.keys():
#             target["query"] = rep_query
#         target["measurement"] = measurement_name
#     dashboard["title"] = measurement_name
#     return dashboard

def generate_dashboard(batch_results,batch_name,influx_client):
    db.write_data(influx_client,batch_results)
    with open('/home/pi/iot-brewing/lib/grafana/base_dashboard.txt', 'r') as file: 
        data = file.read() 
        data = data.replace('ferm_control_test', batch_name)
    dashboard = json.loads(data)
    logger.log('GRAFANA',dashboard)
    return dashboard