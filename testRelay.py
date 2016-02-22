import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pinList = [2, 3, 4, 17, 27, 22, 10, 9 ]
#pinList = [1, 4, 17, 18, 21, 22, 24, 25]
#pinList = [0, 1, 4, 17, 21, 22, 10, 9 ] 
for i in pinList:
	GPIO.setup(i, GPIO.OUT)
	GPIO.output(i, GPIO.HIGH)

SleepTimeL = 2

for i in pinList:
	print i
	GPIO.output(i, GPIO.LOW)
	time.sleep(SleepTimeL)
	GPIO.output(i, GPIO.HIGH)

