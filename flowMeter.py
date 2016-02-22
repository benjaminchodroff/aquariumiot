import serial
import RPi.GPIO as GPIO
import time
import io
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

print "Welcome to Flow Meter"

usbport='/dev/ttyAMA0'
ser=serial.Serial(usbport,9600)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.output(7, GPIO.LOW)
GPIO.output(8, GPIO.LOW)

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

print "enable LED"
ser.write("L,1\r")
ser.write("C,1\r")

#print "programming turbo flow flowmeter"
#ser.write("PRE,T\r")
#ser.write("K,?\r")

print "programming adafruit flow meter"
# Disable the continues mode
ser.write("C,0\r")
# Clear all existing volume
ser.write("CLEAR\r")
# Clear all existing k-values
ser.write("K,CLEAR\r")
# Each pulse equals 2.25 ml
ser.write("K,2.25,1\r")
# Check to see the k-values are set
ser.write("K,?\r")
# Set the volume to measure in mL/minute
ser.write("TK,M\r")
# Check to see the frequency
ser.write("TK,?\r")

# There are 450 pulses per liter

# There is no pullup resistor required
ser.write("P,0\r")
# Check to see the pullup resistor
ser.write("P,?\r")

# Enable continues mode (1 reading a second)
ser.write("C,1\r")

for i in range(0,20): ser_io.readline()

def getLine(ser_io, attempt=5, line=""):
	if (line.strip()=="" and attempt>0):
		attempt=attempt-1
		time.sleep(0.01)
		line=(ser_io.readline()).strip()
		line=getLine(ser_io,attempt,line)
	return line

while True:
	print "Received from sensor:" + getLine(ser_io)

