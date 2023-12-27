import sys
sys.path.insert(1, '/home/pi/ferm_monitor/config')
sys.path.insert(2, '/home/pi/ferm_monitor/lib/bluetooth')

import bluetooth._bluetooth as bluez
import blescan as ble
import config as cfg
from loguru import logger
logger.level("ACQ", no=50, color="<green>")

def get_tilt_data():
    try:
        tiltData = None
        tilt_id = cfg.tilt_id
        tilt_macs = cfg.tilt_macs
        sock = bluez.hci_open_dev(tilt_id)
        ble.hci_le_set_scan_parameters(sock)
        ble.hci_enable_le_scan(sock)
        returnedList = ble.parse_events(sock, 10)
        for beacon in returnedList:
            output = beacon.split(',')
            if output[1] in tilt_macs.keys():
                logger.log('ACQ', 'Tilt with MAC: {} found'.format(output[1]))
                tempc = round(((float(output[2])/10) - 32) * 0.5556,2)
                tiltSG = float(output[3])/10000
                tiltTemp = tempc
                tiltColour = tilt_macs[output[1]]
                tiltData = [tiltSG,tiltTemp,tiltColour]
                logger.log('ACQ','{} Tilt, SG: {}, Temp: {}'.format(tiltColour,tiltSG,tiltTemp))
                return tiltData
            else:
                ble.hci_disable_le_scan(sock)
    except Exception as e:
        logger.log('ACQ_TOOLS',e)
    return tiltData

def format_mqtt(tiltData):
    mqtt_data = {
                "TiltSG": tiltData[0],
                "TiltTemp": tiltData[1],
                "TiltColor": tiltData[2]
                }
    return mqtt_data


def build_json(tiltSG,tiltTemp,tiltColour,tiltOG,tiltBeer,tiltAbv,tiltAA,phI,phF,tgravity,t_volume,a_volume,t_eff,a_eff):
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
    return to_send
