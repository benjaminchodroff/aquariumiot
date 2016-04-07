import config
import ibmiotf.device
from ibmiotf.codecs import jsonIotfCodec

x = 12345

try:
	deviceOptions = {
		"org": organization, 
		"type": deviceType, 
		"id": deviceId, 
		"auth-method": authMethod, 
		"auth-token": authToken }
	deviceCli = ibmiotf.device.Client(deviceOptions)
	deviceCli.connect()
	myData = { 'hello' : 'world', 'x' : x}
	deviceCli.publishEvent(event="greeting", msgFormat="json", data=myData)
except Exception,e:
        print "Unexpected error!"
        print str(e)
        raise
finally: 
	deviceCli.disconnect()

