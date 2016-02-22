#!/bin/bash
SERVER="rtmp://a.rtmp.youtube.com/live2"
KEY=""

while true
do
pkill -9 raspivid
pkill -9 ffmpeg
raspivid -o - -t 0 -ISO 100 -ev 0 -w 1920 -h 1080 -fps 25 -b 5500000 -g 50 -awb off -awbg 1.7,1.8 -st -ae 64,0xff,0x808000 -a "$1" -a 1025 | /home/pi/arm/bin/ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 160k -g 50 -strict experimental -f flv $SERVER/$KEY 
done

