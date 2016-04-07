import config
import time
from datetime import datetime

import ibmiotf.device
from ibmiotf.codecs import jsonIotfCodec

def myCommandCallback(cmd):
	print cmd.data, cmd.command, cmd.timestamp, cmd.format

try:
        deviceOptions = {
                "org": organization,
                "type": deviceType,
                "id": deviceId,
                "auth-method": authMethod,
                "auth-token": authToken }
        deviceCli = ibmiotf.device.Client(deviceOptions)
	deviceCli.connect()
        while True:
		print "checking stuff"
		deviceCli.commandCallback = myCommandCallback
		time.sleep(1)

except Exception,e:
        print "Unexpected error!"
        print str(e)
        raise

finally:
        deviceCli.disconnect()

