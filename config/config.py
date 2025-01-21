tilt_macs =   {
            'a495bb10c5b14b44b5121370f02d74de':'red',
            'a495bb20c5b14b44b5121370f02d74de':'green',
            'a495bb30c5b14b44b5121370f02d74de':'black',
            'a495bb40c5b14b44b5121370f02d74de':'purple',
            'a495bb50c5b14b44b5121370f02d74de':'orange',
            'a495bb60c5b14b44b5121370f02d74de':'blue',
            'a495bb70c5b14b44b5121370f02d74de':'yellow',
            'a495bb80c5b14b44b5121370f02d74de':'pink'
            }

tilt_id = 0

tilt_calibration =0.9891332163

acq_sleep = 900

no_acq_sleep = 10

influxdb_config = {
            'host':'localhost', 
            'port':8086, 
            'user':'', 
            'password':'', 
            'db':'tilt'
            }

mqtt_config = {
            'host':'localhost',
            'port': 1883,
            'topics': ['#'],
            'publish_topic': 'tiltdata'
}

acq_permissive = True
