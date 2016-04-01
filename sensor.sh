#!/bin/bash
. /home/pi/env/iot/bin/activate
/home/pi/env/iot/bin/python /home/pi/allSensor.py >> /home/pi/iot.log 2>&1
