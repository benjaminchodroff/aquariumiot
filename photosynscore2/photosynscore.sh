#!/bin/bash
set -e
ir="/home/pi/ir/"
raw="/home/pi/raw/"
ndvi="/home/pi/ndvi/"
ndviscore="/home/pi/ndviscore/"

photo=$1
photoname=`basename $photo|awk -F '.png' '{print $1}'`

echo "photosyn=\"$photoname\"" > $photoname.score.py 
printf "photosynscore=" >> $photoname.score.py
python photosynscore.py $photo $photoname.ndvi.png >> $photoname.score.py

# Move the photo from ir to raw
mv $photo $raw
# Move the ndvi
mv $photoname.ndvi.png $ndvi
# Move the ndviscore
mv $photoname.score.py $ndviscore

# Update the latest score
ln -sf $raw/$photoname.png latest.raw.png
ln -sf $ndvi/$photoname.ndvi.png latest.ndvi.png 
ln -sf $ndviscore/$photoname.score.py latest.score.py

