import serial
import RPi.GPIO as GPIO
import time
import io
from datetime import datetime
import status
import relay3
import relay4
import relay5
import relay6
import relay7
import latestscore

import ibmiotf.device
from ibmiotf.codecs import jsonIotfCodec

pinList = [2, 3, 4, 17, 27, 22, 10, 9 ]

organization=""
deviceType=""
deviceId=""
authMethod="token"
authToken=""

def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
        GPIO.output(cspin, True)
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

def readMedian(sensor_adc, SPICLK, SPIMOSI, SPIMISO, SPICS, measure=1000):
        measurements=[]
        for i in range(0,measure):
                measurements.append(float(readadc(sensor_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)))
		time.sleep(0.001)
        return float(median(measurements))

def getLine(ser_io, attempt=5, line=""):
        if (line.strip()=="" and attempt>0):
		time.sleep(0.01)
                attempt=attempt-1
                line=(ser_io.readline()).strip()
                line=getLine(ser_io,attempt,line)
        return line

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

try:
        deviceOptions = {
                "org": organization,
                "type": deviceType,
                "id": deviceId,
                "auth-method": authMethod,
                "auth-token": authToken }
        deviceCli = ibmiotf.device.Client(deviceOptions)
	connected = False
	while not connected:
		try:
		        deviceCli.connect()
			connected = True
		except:
			print "Failed to connect to IOT Foundation, trying again in 10 seconds"
			time.sleep(10)
	print "Setting up GPIO"
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(7, GPIO.OUT)
	GPIO.setup(8, GPIO.OUT)

	usbport='/dev/ttyAMA0'
	baudrate='9600'

	ser = serial.Serial(port=usbport,
                         baudrate=baudrate,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         timeout=1)
	ser_io = io.TextIOWrapper(io.BufferedRWPair(ser, ser, 1), encoding='ascii', errors='ignore',
                               newline = '\r',
                               line_buffering = True)

	# Wait this long between each sensor
	waitSensor = 2

	# Buffer input before reading sensor
	waitBuffer = 1

	# Setup
	# Initialize flow meter
	GPIO.output(7, GPIO.LOW)
	GPIO.output(8, GPIO.LOW)
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
	# There is no pullup resistor required
	ser.write("P,0\r")
	# Check to see the pullup resistor
	ser.write("P,?\r")
	# Enable continues mode (1 reading a second)
	ser.write("C,1\r")

	# Initialize pH meter
	GPIO.output(7, GPIO.LOW)
	GPIO.output(8, GPIO.HIGH)

	# Initialize Relays
	for i in pinList:
	        GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, GPIO.HIGH)
#	GPIO.output(pinList[0], GPIO.LOW)
	GPIO.output(pinList[1], GPIO.LOW)
	
	# Initialize Water Level
	# set up the SPI interface pins
	GPIO.setup(SPIMOSI, GPIO.OUT)
	GPIO.setup(SPIMISO, GPIO.IN)
	GPIO.setup(SPICLK, GPIO.OUT)
	GPIO.setup(SPICS, GPIO.OUT)
	# water level sensor
	sensor_adc = 0;

	time.sleep(3)
	
	# Loop
	while True:
		with open('/proc/uptime', 'r') as f:
			uptime_seconds = float(f.readline().split()[0])

		# Check Relay States
		relay1status= not GPIO.input(pinList[0])
        	print "Relay1 - Water Change:",relay1status
        	relay2status= not GPIO.input(pinList[1])
        	print "Relay2 - Co2 Regulator:", relay2status
        	relay3status= not GPIO.input(pinList[2])
        	print "Relay3 - Phosphorus Dosing Pump:",relay3status
        	relay4status= not GPIO.input(pinList[3])
        	print "Relay4 - Potassium Dosing Pump:",relay4status
	        relay5status= not GPIO.input(pinList[4])
        	print "Relay5 - Nitrogen Dosing Pump:",relay5status
	        relay6status= not GPIO.input(pinList[5])
        	print "Relay6 - Iron Dosing Pump:",relay6status
	        relay7status= not GPIO.input(pinList[6])
       		print "Relay7 - Micro Dosing Pump:",relay7status
	        relay8status= not GPIO.input(pinList[7])
	        print "Relay8 - Water Topoff:",relay8status
	
		# Check Flow	
		GPIO.output(7, GPIO.LOW)
		GPIO.output(8, GPIO.LOW)
		time.sleep(waitBuffer)
		ser.flushInput()
		time.sleep(waitSensor)
		volFlow = getLine(ser_io)
		try:
			vol, flow = volFlow.split(",")
			vol = float(vol)
			flow = float(flow)
		except:
			vol = 'unknown'
			flow = 'unknown'
		print "Flow:", flow
		# Check pH
		GPIO.output(7, GPIO.LOW)
		GPIO.output(8, GPIO.HIGH)
		time.sleep(waitBuffer)
		ser.flushInput()
		time.sleep(waitSensor)
		pH = getLine(ser_io)
		try:
			pH = float(pH)
		except:
			pH = 'unknown'

		print "pH:", pH
		# Control CO2
		if (pH < 6.25):
			print "CO2 OFF"
			GPIO.output(pinList[1], GPIO.HIGH)
		else:
			print "CO2 ON"
			GPIO.output(pinList[1], GPIO.LOW)

		# Check Temperature
		GPIO.output(7, GPIO.HIGH)
		GPIO.output(8, GPIO.LOW)
		time.sleep(waitBuffer)
		ser.flushInput()
		time.sleep(waitSensor)
		temp = getLine(ser_io)
		try:
			temp = float(temp)
		except:
			temp = 'unknown'

		print "Temperature:",temp

		# Check Water Level
		level=(readMedian(sensor_adc, SPICLK, SPIMOSI, SPIMISO, SPICS, measure=500)-109)/1.71

		print "Level:",str(level)	
		# Publish data to IOTF
		reload(status)
		reload(relay3)
		reload(relay4)
		reload(relay5)
		reload(relay6)
		reload(relay7)
		reload(latestscore)
		myData = { 	'datetime': datetime.utcnow().isoformat(),
				'alerting': status.alerting,
				'uptime': uptime_seconds,
				'relay1': relay1status, 
				'relay2': relay2status, 
				'relay3': relay3status, 
				'relay4': relay4status, 
				'relay5': relay5status, 
				'relay6': relay6status, 
				'relay7': relay7status, 
				'relay8': relay8status, 
				'water_vol': vol,
				'water_flow': flow,
				'water_ph':  pH, 
				'water_temp': temp,
				'water_level': level,
				'photosynthesis_score': latestscore.photosynscore,
				'water_lastChanged': status.water_lastChanged,
				'phosphorus_lastAdded': relay4.relay4LastAdded,
				'potassium_lastAdded': relay5.relay5LastAdded,
				'nitrogen_lastAdded': relay3.relay3LastAdded,
				'micro_lastAdded': relay7.relay7LastAdded,
				'iron_lastAdded': relay6.relay6LastAdded,
				'phosphorus_lastAddedVolume': relay4.relay4Volume,
				'potassium_lastAddedVolume': relay5.relay5Volume,
				'nitrogen_lastAddedVolume': relay3.relay3Volume,
				'micro_lastAddedVolume': relay7.relay7Volume,
				'iron_lastAddedVolume': relay6.relay6Volume,
				'filter1_lastCleaned': status.filter1_lastCleaned,
				'filter2_lastCleaned': status.filter2_lastCleaned,
				'co2_lastReplaced': status.co2_lastReplaced
				 }
        	deviceCli.publishEvent(event="status", msgFormat="json", data=myData)
except KeyboardInterrupt:  
	print "Closing Sensor Connections"  
  
except Exception,e:  
	print "Unexpected error!"
        print str(e)
	raise 
finally:  
	GPIO.cleanup() 
        deviceCli.disconnect()

