#!/bin/bash
set -e -u
/home/pi/alerts.sh False
python /home/pi/removeWater.py 30000
python /home/pi/addWater.py 30000
/home/pi/alerts.sh True
