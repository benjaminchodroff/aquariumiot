#!/bin/sh

#hdmi_on.sh - custom script to turn HDMI on 

#get the current tv state
tvstate=`tvservice -s | grep HDMI | wc -l`

#only turn on if its not already on
if [ "$tvstate" -eq 0 ] 
then
#   tvservice --explicit="DMT 87"
   tvservice -p
   fbset -depth 8
   fbset -depth 16
   DISPLAY=:0 xrefresh
else
   echo "HDMI already on";
fi

exit;

