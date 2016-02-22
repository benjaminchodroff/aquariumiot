#!/bin/bash
value=$1
if [ $value == "True" ]; then
echo "Alerting Enabled"
sed -i 's/alerting=\".*\"/alerting=\"True\"/g' /home/pi/status.py
elif [ $value == "False" ]; then
echo "Alerting Diabled"
sed -i 's/alerting=\".*\"/alerting=\"False\"/g' /home/pi/status.py
else
echo "You must specify ./maintenance.sh [True/False]"
fi
