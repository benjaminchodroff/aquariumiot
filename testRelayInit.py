import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)

pinList = [2, 3, 4, 17, 27, 22, 10, 9 ]
GPIO.setup(pinList[0], GPIO.OUT)
GPIO.setup(pinList[1], GPIO.OUT)
GPIO.output(pinList[0], GPIO.LOW)
GPIO.output(pinList[1], GPIO.LOW)
time.sleep(10)
GPIO.output(pinList[0], GPIO.HIGH)
GPIO.output(pinList[1], GPIO.HIGH)
