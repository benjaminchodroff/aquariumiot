import time
import RPi.GPIO as GPIO

# Two Point Calibration #
calHigh = { "level": 26.0, "sensor": 746.5, "reference": 699.0 }
calLow = { "level": 15.0, "sensor": 620.5, "reference": 699.0 }
#################
from numpy import ones,vstack
from numpy.linalg import lstsq
points = [
	(calHigh['sensor'],calHigh['level']),
	(calLow['sensor'],calLow['level'])
]
x_coords, y_coords = zip(*points)
A = vstack([x_coords,ones(len(x_coords))]).T
m, c = lstsq(A, y_coords)[0]
#print "Line Solution is y = {m}x + {c}".format(m=m,c=c)

def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0

# Bit banged clock
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
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

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# water level sensor
sensor_adc = 0;

# reference voltage (560 ohms with reference 1.2k ohm resistor to ground)
reference_adc = 1;
null_adc = 2;

def readMedian(sensor_adc, SPICLK, SPIMOSI, SPIMISO, SPICS, measure=100):
	measurements=[]
	for i in range(0,measure):
		measurements.append(float(readadc(sensor_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)))
		time.sleep(0.01)
	return float(median(measurements))

def readWaterLevel(attempts=3):
	refmedian = readMedian(reference_adc, SPICLK, SPIMOSI, SPIMISO, SPICS, measure=10)
	reference=699
	median=readMedian(sensor_adc, SPICLK, SPIMOSI, SPIMISO, SPICS, measure=500)-(reference-refmedian)
#	print 'median',median
#	print 'refmedian',refmedian
	level=m*median + c
	if(level<0 or level>100):
		if(attempts>0):
			attempts=attempts-1
#			print "trying again",attempts
			level=readWaterLevel(attempts)
	return level

if __name__ == "__main__" :
	print "sensor:", str(readWaterLevel())


