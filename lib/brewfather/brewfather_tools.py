# -*- coding: utf-8 -*-
import requests
import json
import base64
import time
from datetime import datetime
from loguru import logger
logger.level("BF", no=50, color="<white>")


def b64_encode(uid,key):
    message = uid + ':' + key
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def get_token():
    key = 'nLSqjBvSuTx71ZzfOmTyEzpcffhieYjuyAJfaUmtncd80NCfTDLlM6i1voffmRqr'
    uid = 'LWMuzXegkOfJX25UXwDU5lFWE5w2'
    token = b64_encode(uid,key)
    return token 

def get_full_receipe(recipe_id):
    token = get_token()
    endpoint = 'https://api.brewfather.app/v2/recipes/' + recipe_id
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': "Basic " + token
              }
    full_recipe = requests.get(endpoint, headers=headers).json()
    return full_recipe

def get_recipe_id(recipe_name):
    recipe_id = None
    try:
        token = get_token()
        endpoint = 'https://api.brewfather.app/v2/recipes/'
        headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': "Basic " + token
                }
        recipes = requests.get(endpoint, headers=headers).json()
        for recipe in recipes:
            if recipe['name'] == recipe_name:
                recipe_id = recipe['_id']
        if recipe_id is None:
            logger.log('BF','Recipe name not found')
    except Exception as e:
        logger.log('BF','ERROR: {}'.format(e))
    return recipe_id

def get_last_batch_id():
    batch_numbers = []
    try:
        token = get_token()
        endpoint = 'https://api.brewfather.app/v2/batches/'
        headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': "Basic " + token
                }
        batches = requests.get(endpoint, headers=headers).json()
        for batch in batches:
            batch_numbers.append(batch['batchNo'])
        last_batch = max(batch_numbers)
        for batch in batches:
            if batch['batchNo'] == last_batch:
                batch_id = batch['_id']
                batch_name = '{} - {}'.format(last_batch,batch['recipe']['name'])
    except Exception as e:
        logger.log('BF','ERROR: {}'.format(e))
    return batch_id,batch_name

def get_batch_data(batch_id):
    try:
        token = get_token()
        endpoint = 'https://api.brewfather.app/v2/batches/{}'.format(batch_id)
        headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': "Basic " + token
                }
        batch_data = requests.get(endpoint, headers=headers).json()
    except Exception as e:
        logger.log('BF','ERROR: {}'.format(e))
    return batch_data

def get_batch_results(batch_data,batch_name):
    try:
        ferm_start_date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(batch_data['fermentationStartDate']/1000)).split(' ')[0]
        brew_date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(batch_data['brewDate']/1000)).split(' ')[0]
        bottlingdate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(batch_data['bottlingDate']/1000)).split(' ')[0]
        results = {}
        results['measurement'] = batch_name
        results['tags'] = {'recipe':"test recipe",'tilt':"tilt_color"}
        results['fields'] = {
                            "fermentationStartDate":str(ferm_start_date),
                            "brewDate":str(brew_date),
                            "bottlingDate":str(bottlingdate),
                            "measuredBoilSize":str(batch_data.get('measuredBoilSize')) + ' L',
                            "measuredPreBoilGravity":str(batch_data.get('measuredPreBoilGravity')),
                            "estimatedIbu":str(batch_data.get('estimatedIbu')),
                            "measuredMashEfficiency":str(batch_data.get('measuredMashEfficiency')) + ' %',
                            "estimatedOg":str(batch_data.get('estimatedOg')),
                            "estimatedFg":str(batch_data.get('estimatedFg')),
                            "measuredOg":str(batch_data.get('measuredOg')),
                            "measuredBatchSize":str(batch_data.get('measuredBatchSize')) + ' L',
                            "measuredEfficiency":str(batch_data.get('measuredEfficiency')) + ' %',
                            "status": str(batch_data.get('status')),
                            "mashPH": str(batch_data.get('measuredMashPh')),
                            "estimatedBuGuRatio": str(batch_data.get('estimatedBuGuRatio')),
                            "measuredAbv": str(batch_data.get('measuredAbv')) + ' ABV',
                            "measuredAttenuation": str(batch_data.get('measuredAttenuation')) + ' %'
                            }
        bf_data = [results]
    except Exception as e:
        bf_data = []
        logger.log('BF','ERROR: {}'.format(e))
    return bf_data

def get_bf_data(batch_id,batch_name):
    tilt_permissive = False
    batch_data = get_batch_data(batch_id)
    bf_data = get_batch_results(batch_data,batch_name)
    batch_status = bf_data[0]['status']
    if batch_status == 'Fermenting' or batch_status == 'Conditioning':
        tilt_permissive = True
    return bf_data, tilt_permissive

def get_recipe_info(full_recipe):
    name = full_recipe['name']
    style = full_recipe['style']['name']
    abv = str(full_recipe['abv']) + '%'
    author = full_recipe['author']
    stype = full_recipe['type']
    return name, style, abv, author, stype

def get_equipment_info(full_recipe):
    name = full_recipe['equipment']['name']
    mash_eff = str(full_recipe['mashEfficiency']) + '%'
    batch_volume = str(full_recipe['batchSize']) + ' L'
    boil_time = str(full_recipe['boilTime']) + ' min'
    return name,mash_eff, batch_volume, boil_time

def get_water_volumes_info(full_recipe):
    total_water = str(full_recipe['data']['totalWaterAmount']) + ' L'
    mash_water = str(full_recipe['data']['mashWaterAmount']) + ' L'
    sparge_water = str(full_recipe['data']['spargeWaterAmount']) + ' L'
    boil_volume = str(full_recipe['boilSize']) + ' L'
    postboil_volume = str(round(full_recipe['equipment']['postBoilKettleVol'],2)) + ' L'
    return total_water, mash_water, sparge_water,boil_volume, postboil_volume

def get_vitals_info(full_recipe):
    preboil_g = str(round(full_recipe['preBoilGravity'],3))
    original_g = str(round(full_recipe['og'],3))
    final_g = str(round(full_recipe['fg'],3))
    ibu = str(round(full_recipe['ibu'],2))
    color = str(full_recipe['color']) + ' SRM'
    dryhop_ratio_int = round(full_recipe['sumDryHopPerLiter'],2)
    dryhop_ratio = str(dryhop_ratio_int) + ' g/L' + ' or ' + str(round(dryhop_ratio_int * 0.133526,2)) + ' oz/gal'
    return preboil_g, original_g, final_g, ibu, dryhop_ratio, color

def get_mash_info(full_recipe):
    mash_step_list = []
    strike_temp = str(full_recipe['data']['strikeTemp']) + ' C'
    for step in full_recipe['mash']['steps']:
        mash_step_list.append(str(step['name']) + ' ---' + str(step['stepTemp']) + ' C' + ' ---' + str(step['stepTime']) + ' min')
    return strike_temp, mash_step_list

def get_malts_info(full_recipe):
    malt_list = []
    total_malts = 'Malts ' + '(' + str(full_recipe['data']['mashFermentablesAmount']) + ' kg' + ')'
    for fermentable in full_recipe['fermentables']:
        amount = str(fermentable['amount'])
        percentage = str(fermentable['percentage'])
        name = fermentable['name']
        mtype = fermentable['type']
        color = str(fermentable['color'])
        malt_list.append(amount + ' kg ' + '(' + percentage + ' %)' + ' --- ' + name + ' --- ' + mtype + ' --- ' + color + ' SRM' )
    return total_malts, malt_list

def get_hops_info(full_recipe):
    hop_list = []
    total_hops = 'Hops ' + '(' + str(full_recipe['hopsTotalAmount']) + ' g' + ')'
    for hop in full_recipe['hops']:
        amount = str(hop['amount'])
        ibu = str(hop['ibu'])
        name = hop['name']
        alpha = str(hop['alpha'])
        use = hop['use']
        time = str(hop['time'])
        if use == 'Dry Hop':
            day = hop['day']
            hop_list.append(amount + ' g ' + '(' + ibu + ' IBU)' + ' --- ' + name + ' ' + alpha + '%' ' --- ' + use + ' --- ' + 'day ' + time)
        elif use == 'Aroma':
            hop_list.append(amount + ' g ' + '(' + ibu + ' IBU)' + ' --- ' + name + ' ' + alpha + '%' ' --- ' + use + ' --- ' + time + ' min' + ' whirpool')
        else:
            hop_list.append(amount + ' g ' + '(' + ibu + ' IBU)' + ' --- ' + name + ' ' + alpha + '%' ' --- ' + use + ' --- ' + time + ' min')
    whirpool_temp = 'Whirpool at ' + str(full_recipe['avgWeightedHopstandTemp']) + ' C'
    return total_hops, hop_list, whirpool_temp

def get_water_additions_info(full_recipe):
    misc_list = []
    for misc in full_recipe['miscs']:
        amount = str(misc['amount'])
        name = misc['name']
        use = misc['use']
        unit = misc['unit']
        misc_list.append(amount + ' ' + unit + ' --- ' + name + ' --- ' + use )
    return misc_list

def get_yeast_info(full_recipe):
    name = full_recipe['yeasts'][0]['name']
    laboratory = full_recipe['yeasts'][0]['laboratory']
    max_att = str(full_recipe['yeasts'][0]['maxAttenuation'])
    full_name = laboratory + ' ' + name + ' ' + max_att + '%'
    return full_name

def get_fermentation_info(full_recipe):
    ferm_step_list = []
    name = full_recipe['fermentation']['name']
    for step in full_recipe['fermentation']['steps']:
        ftype = step['type']
        temp = str(step['displayStepTemp'])
        time = str(step['stepTime'])
        ferm_step_list.append(ftype + ' --- ' + temp + ' C' + ' --- ' + time + ' days')
    return name, ferm_step_list
    
def get_carbonation_info(full_recipe):
    vol = str(full_recipe['carbonation']) + ' CO2-vol'
    return vol 

def create_recipe(recipe_name):
    logger.log('BF','Creating recipe panel')
    try:
        recipe_id = get_recipe_id(recipe_name)
        full_recipe = get_full_receipe(recipe_id)
        recipe_info = get_recipe_info(full_recipe)
        equipment_info = get_equipment_info(full_recipe)
        water_volumes_info = get_water_volumes_info(full_recipe)
        vitals_info = get_vitals_info(full_recipe)
        mash_info = get_mash_info(full_recipe)
        malts_info = get_malts_info(full_recipe)
        hops_info = get_hops_info(full_recipe)
        water_additions_info = get_water_additions_info(full_recipe)
        yeast_info = get_yeast_info(full_recipe)
        fermentation_info = get_fermentation_info(full_recipe)
        carbonation_info = get_carbonation_info(full_recipe)
        filename = recipe_name + '.txt'
        with open('/home/pi/brewing-monitor/lib/grafana/recipes/' + filename, 'w') as file:
            file.write(recipe_info[0] + '\n' 
                    + '-----------' + '\n\n'
                    + recipe_info[1] + '\n\n' 
                    + recipe_info[2] + '\n\n'
                    + 'Recipe by: ' + recipe_info[3] + '\n\n' 
                    + recipe_info[4] + '\n\n'
                    )
            file.write('### ' + equipment_info[0] + '\n\n'
                    + 'Mash efficiency: ' + equipment_info[1] + '\n\n'
                    + 'Batch volume: ' + equipment_info[2] + '\n\n'
                    + 'Boil time: ' + equipment_info[3] + '\n\n' 
                    )
            file.write('### ' + 'Water Volumes' + '\n\n'
                    + 'Total Water: ' + water_volumes_info[0] + '\n\n'
                    + 'Mash Water: ' + water_volumes_info[1] + '\n\n' 
                    + 'Sparge Water: ' + water_volumes_info[2] + '\n\n' 
                    + 'Pre-boil Water: ' + water_volumes_info[3] + '\n\n'
                    + 'Post-boil Water: ' + water_volumes_info[4] + '\n\n' 
                    )
            file.write('### ' + 'Vitals' + '\n\n'
                    + 'Pre-boil Gravity: ' + vitals_info[0] + '\n\n'
                    + 'Original Gravity: ' + vitals_info[1] + '\n\n'
                    + 'Final Gravity: ' + vitals_info[2] + '\n\n' 
                    + 'IBU: ' + vitals_info[3] + '\n\n' 
                    + 'DryHop ratio: ' + vitals_info[4] + '\n\n'
                    + 'Color: ' + vitals_info[5] + '\n\n' 
                    )
            file.write('### ' + 'Mash' + '\n\n'
                    + 'Strike Temp --- ' + mash_info[0] + '\n\n'
                    )
            for step in mash_info[1]:
                file.write(step + '\n\n')
            file.write('### ' + malts_info[0] + '\n\n')
            for malt in malts_info[1]:
                file.write(malt + '\n\n')
            file.write('### ' + hops_info[0] + '\n\n')
            for hop in hops_info[1]:
                file.write(hop + '\n\n')
            file.write('### ' + 'Water Additions' + '\n\n')
            for add in water_additions_info:
                file.write(add + '\n\n')
            file.write('### ' + 'Yeast' + '\n\n'
                    + yeast_info + '\n\n'
                    )
            file.write('### ' + 'Fermentation' + '\n\n')
            file.write(fermentation_info[0] + '\n\n')
            for step in fermentation_info[1]:
                file.write(step + '\n\n')      
            file.write('### ' + 'Carbonation' + '\n\n'
                    + carbonation_info + '\n\n'
                    )
        with open('/home/pi/brewing-monitor/lib/grafana/recipes/' + filename, 'r') as opened_file:
            recipe_panel = opened_file.read()
        logger.log('BF','Recipe panel generated')
    except Exception as e:
        logger.log('BF','ERROR: {}'.format(e))
    return recipe_panel

def send_to_brewfather(bf_data):
    url = 'http://log.brewfather.net/stream?id=juqWHHX8re7Sgu'
    headers = {"Content-Type": "application/json"}
    try:
        p = requests.post(url, headers=headers, data=json.dumps(bf_data))
        if p.status_code == 200:
            logger.log('BF','Succesfully inserted data in BrewFather')
        else:
            logger.log('BF','Bad response trying to send data to BrewFather {}'.format(p.status_code))
    except Exception as e:
        logger.log('BF','ERROR: {}'.format(e))
    return