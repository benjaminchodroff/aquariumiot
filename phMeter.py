import serial
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

print "Welcome to pH Meter"

usbport='/dev/ttyAMA0'
ser=serial.Serial(usbport,9600)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.output(7, GPIO.LOW)
GPIO.output(8, GPIO.HIGH)

print "enable LED"
#ser.write("Factory\r")
ser.write("T,?\r")
#ser.write("T,21.0\r")
ser.write("L,1\r")
ser.write("C,1\r")
#ser.write("Cal,clear\r")
#ser.write("Cal,mid,7.00\r")
#ser.write("Cal,low,4.00\r")
#ser.write("Cal,high,10.00\r")
ser.write("Cal,?\r")
ser.write("SLOPE,?\r")

line=""

while True:
	data = ser.read()
	if(data=="\r"):
		print "Received from sensor:" + line
		line=""
	else:
		line=line+data

	
