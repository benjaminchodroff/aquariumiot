#!/bin/bash
value=$1
sed -i 's/waterStage=.*/waterStage='$value'/g' /home/pi/status.py
