import requests
import json

import sys
sys.path.insert(1, '/home/pi/brewing-monitor/lib/influxdb')
sys.path.insert(2, '/home/pi/brewing-monitor/lib/brewfather')

import influxdb_tools as db
import brewfather_tools as bf

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
        payload = {"dashboard": dashboard,
                   "overwrite": True}
        p = requests.post(url, headers=headers, json=payload)
        if p.status_code == 200:
            logger.log('GRAFANA','Succesfully updated dashboard')
        else:
            logger.log('GRAFANA','Bad response trying to send dashboard: {}'.format(p.status_code))
    except Exception as e:
        logger.log('GRAFANA','ERROR: {}'.format(e))
    return

def generate_dashboard(batch_name):
    recipe = batch_name.split('-')[1].strip()
    recipe_panel = bf.create_recipe(recipe)
    with open('/home/pi/brewing-monitor/lib/grafana/base_dashboard.txt', 'r') as file: 
        data = file.read() 
        data = data.replace('batch_data', batch_name)
        data = data.replace('tilt_data', '{} - tilt'.format(batch_name))
    dashboard = json.loads(data)
    dashboard['title'] = batch_name
    dashboard['tags'] = [recipe]
    for panel in dashboard["panels"]:
        if panel.get('title') == 'Recipe':
            panel['options']['content'] = recipe_panel
    send_dashboard_to_grafana(dashboard)
    return