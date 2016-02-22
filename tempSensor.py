import serial
import RPi.GPIO as GPIO
import time
import io

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)
GPIO.output(8, GPIO.LOW)

print "Welcome to Temperature Sensor"

usbport='/dev/ttyAMA0'
baudrate='9600'

ser = serial.Serial(port=usbport,
                         baudrate=baudrate,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         timeout=1)
ser_io = io.TextIOWrapper(io.BufferedRWPair(ser, ser, 1),  
                               newline = '\r',
                               line_buffering = True)
# Ensure we are configured for 9600 baud
#ser.write("z4\r")
ser.write("S?\r")
while True:
	print ser_io.readline()
	time.sleep(1)

	
