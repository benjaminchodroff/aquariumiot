import RPi.GPIO as GPIO
import time
import sys
from waterSensor import readWaterLevel
GPIO.setmode(GPIO.BCM)

pinList = [2, 3, 4, 17, 27, 22, 10, 9 ]
maxHeight = 27.5

try:
	sleep=int(sys.argv[1])
	GPIO.setup(pinList[7], GPIO.OUT)
	GPIO.output(pinList[7], GPIO.HIGH)
	print "Adding Water until water level reaches",maxHeight,"cm or",sleep,"seconds elapse"

	GPIO.output(pinList[7], GPIO.LOW)
	for i in range(0,sleep):
		time.sleep(1)
		level = float(readWaterLevel())
		print "level=",level,"\tseconds=",i
		if (level>=maxHeight):
			print "Maximum water level of",maxHeight,"cm reached!"
			break
		if (level<=0):
			print "The water level was less than 0. ERROR!"
			break
	GPIO.output(pinList[7], GPIO.HIGH)

except KeyboardInterrupt:
        print "Stopping Water"

except:
        print "Unexpected error!"
        raise

finally:
	GPIO.output(pinList[7], GPIO.HIGH)
	print "Water Off"


