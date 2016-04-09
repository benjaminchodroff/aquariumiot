import config
import serial
import RPi.GPIO as GPIO
import time
import io
from datetime import datetime
from subprocess import call
import status
import relay3
import relay4
import relay5
import relay6
import relay7
import latestscore
from waterSensor import readWaterLevel
import ibmiotf.device
from ibmiotf.codecs import jsonIotfCodec

pinList = [2, 3, 4, 17, 27, 22, 10, 9 ]

def myCommandCallback(cmd):
	if (cmd.command == "control"):
		# {u'd': {u'count': u'1', u'dosing': u'Phosphorus'}}
		if('dosing' in cmd.data['d']):	
			dosing=cmd.data['d']['dosing']
			count=cmd.data['d']['count']
			print "control=",dosing,count
			if(dosing=="Nitrogen"):
				relay="3"
			elif(dosing=="Phosphorus"):
				relay="4"
			elif(dosing=="Potassium"):
				relay="5"
			elif(dosing=="Iron"):
				relay="6"
			elif(dosing=="Micro"):
				relay="7"
			else:
				relay="8"
			call("python /home/pi/addDosing.py "+str(count)+" "+str(relay)+"&",shell=True)
		elif('toggleAlerting' in cmd.data['d']):
			print "control=toggleAlerting"
			alerting=status.alerting
			if(alerting=="True"):
				alerting="False"
			else:
				alerting="True"
			call("/home/pi/alerts.sh "+alerting+"&",shell=True)
		elif('waterChange' in cmd.data['d']):
			print "control=waterChange"
			call("/home/pi/waterStage.sh 1", shell=True)
		elif('waterTopoff' in cmd.data['d']):
			print "control=waterTopoff"
			call("/home/pi/waterStage.sh 2",shell=True) 
		else:
			print "unknown command" 

def getLine(ser_io, attempt=3, line=""):
        if (line.strip()=="" and attempt>0):
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
                "org": config.organization,
                "type": config.deviceType,
                "id": config.deviceId,
                "auth-method": config.authMethod,
                "auth-token": config.authToken }
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

	# Initialize Relays off
	for i in pinList:
	        GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, GPIO.HIGH)
	
	time.sleep(3)

	# Loop
	while True:
		with open('/proc/uptime', 'r') as f:
			uptime_seconds = float(f.readline().split()[0])

		# Check for commands
		deviceCli.commandCallback = myCommandCallback
	
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
		for x in range(0,5):
			try:	
				vol, flow = volFlow.split(",")
				vol = float(vol)
				flow = float(flow)
				break
			except Exception as e:
				time.sleep(1)
				print e,volFlow
				# if we error out, just use the last flow we had... not ideal
				#flow=-1.0
				#vol=-1.0
				# TODO: error control
		print "Flow:", flow
		# Check pH
		GPIO.output(7, GPIO.LOW)
		GPIO.output(8, GPIO.HIGH)
		time.sleep(waitBuffer)
		ser.flushInput()
		time.sleep(waitSensor)
		try:
			pH = float(getLine(ser_io))
		except:
			#if we error out, just use the last pH we had
			#pH = -1.0
			# TODO: error control
			pH = pH

		print "pH:", pH
		# Control CO2
		if (pH < 6.5):
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
		try:
			temp = float(getLine(ser_io))
		except:
			# if we error out, just use the last temp we had
			#temp = -1.0
			# TODO: error control
			temp = temp
		print "Temperature:",temp

		# Check Water Level
		try:
			level=readWaterLevel(attempts=3)
		except:
			print "Exception in finding level"
		if(level<0 or level>100):
			# This should never happen, but let's return -1
			# TODO: error control
			level=-1.0

		print "Level:",str(level)	
		# Water Addition Change
		# 0 - no removal (stop all water removal and addition devices)
		# 1 - remove water until 15.5 cm (water removal started, water addition stopped)
		# 2 - add water until 27.5 cm (water removal stopped, water addition started)
		if(status.waterStage==0):
			print "waterStage 0"
			GPIO.output(pinList[0], GPIO.HIGH) # Turn off water removal
			GPIO.output(pinList[7], GPIO.HIGH) # Turn off water addition
		if(status.waterStage==1):
			print "waterStage 1"
			print "Disabling alerts"
			call("/home/pi/alerts.sh False", shell=True)
			GPIO.output(pinList[7], GPIO.HIGH) # Turn off water addition (safety check)
			if(level>=status.waterMin):
				print "Removing water"
				GPIO.output(pinList[0], GPIO.LOW) # Turn on water removal
			else: 
				print "Water level reached minimum"
				print "Turning off water removal"
				GPIO.output(pinList[0], GPIO.HIGH) # Turn off water removal
				print "Setting waterStage 2"
				call("/home/pi/waterStage.sh 2", shell=True)
		if(status.waterStage==2):
			print "waterStage 2"
			GPIO.output(pinList[0], GPIO.HIGH) # Turn off water removal (safety check)
			if(level<=status.waterMax):
				print "Adding water"
				GPIO.output(pinList[7], GPIO.LOW) # Turn on water addition
			else:
				print "Water level reached max"
				print "Turning off water"
				GPIO.output(pinList[7], GPIO.HIGH) # Turn off water addition
				print "Setting waterStage 0"
				call("/home/pi/waterStage.sh 0", shell=True)
				print "Enabling alerts"
				call("/home/pi/alerts.sh True", shell=True)
			

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
	print "Turn off all devices"
	for i in pinList:
                GPIO.setup(i, GPIO.OUT)
                GPIO.output(i, GPIO.HIGH)
	GPIO.cleanup() 
        print "Disconnect from IBM IOT Foundation"
	deviceCli.disconnect()
	print "Goodbye!"


