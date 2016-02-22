import RPi.GPIO as GPIO
import time
import sys
import datetime

GPIO.setmode(GPIO.BCM)

pinList = [2, 3, 4, 17, 27, 22, 10, 9 ]
try:
	sleep=int(sys.argv[1])
	relay = int(sys.argv[2])
	GPIO.setup(pinList[relay-1], GPIO.OUT)
	GPIO.output(pinList[relay-1], GPIO.HIGH)
	amount = float(sleep)/10*2.5
	print "Dosing #",relay,"\tAmount:",str(amount),"mL"
	with open("/home/pi/relay"+str(relay)+".py", "w") as myfile:
	    myfile.write("relay"+str(relay)+"LastAdded=\""+str(datetime.datetime.utcnow().isoformat())+"\"\nrelay"+str(relay)+"Volume="+str(amount)+"\n")
	GPIO.output(pinList[relay-1], GPIO.LOW)
	for i in range(0,sleep):
		print i
		time.sleep(0.1)
	GPIO.output(pinList[relay-1], GPIO.HIGH)

except KeyboardInterrupt:
        print "Stopping"

except Exception, e:
        print "Unexpected error!"
	print e
        raise

finally:
	GPIO.output(pinList[relay-1], GPIO.HIGH)
	print "Relay Off"


