import RPi.GPIO as GPIO
import time
import sys
from waterSensor import readWaterLevel
GPIO.setmode(GPIO.BCM)

pinList = [2, 3, 4, 17, 27, 22, 10, 9 ]
minHeight =15.5 

try:
	sleep=int(sys.argv[1])
	GPIO.setup(pinList[0], GPIO.OUT)
	GPIO.output(pinList[0], GPIO.HIGH)
	print "Removing Water until water level reaches",minHeight,"cm or",sleep,"seconds elapse"

	GPIO.output(pinList[0], GPIO.LOW)
	for i in range(0,sleep):
		time.sleep(1)
		level = float(readWaterLevel())
		print "level=",level,"\tseconds=",i
		if (level<=minHeight):
			print "Minimum water level of",minHeight,"cm reached!"
			break
		if (level<=0):
			print "The water level was less than 0. ERROR!"
			break
	GPIO.output(pinList[0], GPIO.HIGH)

except KeyboardInterrupt:
        print "Stopping Water Change"

except:
        print "Unexpected error!"
        raise

finally:
	GPIO.output(pinList[0], GPIO.HIGH)
	print "Water Change Off"


