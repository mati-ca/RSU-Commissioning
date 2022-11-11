# python3 commission.py 192.168.0.54 Sdsm On - CV2X Radios ON
# python3 commission.py 192.168.0.54 Sdsm Off - CV2X Radios OFF
# python3 commission.py 192.168.0.54 Psm - On - CV2X Radios ON
# python3 commission.py 192.168.0.54 Psm - Off - CV2X Radios OFF

import isdigit # pip3 install isdigit
import paramiko # pip3 install paramiko
import sys
import os
import getpass

def do_on_rsu(arg):
	print(arg)
	stdin, stdout, stderr = client.exec_command(arg)
	result = ''
	for line in stdout:
		result += line
		print(line[:-1])
	return result[:-1]
# Welcome to RSU Commissioning Script
print (64 * "*")
print (3 * "*")
print ((3 * "*") + (10 * " ") + "Welcome to RSU Commissioning Script")
print (3 * "*")
print (64 * "*")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

hostname=sys.argv[1]
client.connect(hostname, username="root",
            key_filename="/home/matifrenkel/.ssh/id_rsa_rsu", password='xxxx',
            disabled_algorithms=dict(pubkeys=["rsa-sha2-512", "rsa-sha2-256"])
            )

do_on_rsu("muci cff set sensorAdapters.udpAdapter.enable true")
do_on_rsu("muci cff set sensorAdapters.udpAdapter.port 12321")
do_on_rsu("muci saf set native.sensorSharing.enable true")
do_on_rsu("muci saf set native.sensorSharing.excludeV2xSendingObjects false")

if "sdsm" in sys.argv[2].lower():
	do_on_rsu("muci its set sdsmTx.enable true")
	do_on_rsu("muci its set sdsmTx.radioInterface 'default'")
	do_on_rsu("muci saf set native.sensorSharing.mode Sdsm")

if "psm" in sys.argv[2].lower():
	do_on_rsu("muci saf set native.sensorSharing.mode Psm")

if "on" in sys.argv[3].lower():
	do_on_rsu("muci its set radio.qc9150.enable true")

if "off" in sys.argv[3].lower():
	do_on_rsu("muci its set radio.qc9150.enable false")


# only change the camera position if the navigation is valid
nav_is_valid = do_on_rsu("muci stat navigation.isValid")
if "true" in nav_is_valid:
	# the latitude from navigation stats (it is an int)
	lat = do_on_rsu("muci stat navigation.latitude").split(' ')[-2]
	lat = lat[:-7] + "." + lat[-7:]
	# set latitude in decimal
	do_on_rsu("muci cff set sensorAdapters.camera.position.lat " + lat)
	# read back the latitude to check that the set worked right
	do_on_rsu("muci cff get sensorAdapters.camera.position.lat")
	# the logitude from navigation stats (it is an int)
	lon = do_on_rsu("muci stat navigation.longitude").split(' ')[-2]
	lon = lon[:-7] + "." + lon[-7:]
	# set logitude in decimal
	do_on_rsu("muci cff set sensorAdapters.camera.position.lon " + lon)
	# read back the longitude to check that the set worked right
	do_on_rsu("muci cff get sensorAdapters.camera.position.lon")
else:
	print("navigation isn't valid - camera navigation not set")

do_on_rsu("unplugged-rt-restart.sh")

#check firewall
found_rule = False
index = 0
while(True):
	result = do_on_rsu("uci get firewall.@rule[" + str(index) + "]")
	if "rule" in result:
		dest_port = do_on_rsu("uci get firewall.@rule[" + str(index) + "].dest_port")
		if dest_port.isdigit() and int(dest_port) == 12321:
			proto = do_on_rsu("uci get firewall.@rule[" + str(index) + "].proto")
			src = do_on_rsu("uci get firewall.@rule[" + str(index) + "].src")
			if "udp" in proto and "wan" in src:
				found_rule = True
				break
	else:
		break
	index += 1

# add the rule if it isn't found
if not found_rule:
	do_on_rsu("uci add firewall rule")
	do_on_rsu("uci set firewall.@rule[-1].name='UDP Adapter'")
	do_on_rsu("uci set firewall.@rule[-1].src='wan'")
	do_on_rsu("uci set firewall.@rule[-1].proto='udp'")
	do_on_rsu("uci set firewall.@rule[-1].target='ACCEPT'")
	do_on_rsu("uci set firewall.@rule[-1].dest_port='12321'")
	do_on_rsu("uci commit")
	do_on_rsu("/etc/init.d/firewall restart")

# lastly - change the password - after this client.connect will have to be called again with the new password
def IsPasswordValid(password):
	if (len(password) > 5 and len(password) < 20):
		lowerCase = False
		upperCase = False
		num = False
		special = False

		for char in password:
			if (char.isdigit()):
				num = True
			if (char.islower()):
				lowerCase = True
			if (char.isupper()):
				upperCase = True
			if (not char.isalnum()):
				special = True
		return lowerCase and upperCase and num and special
	else: return False

print (64 * "*")
print (3 * "*")
print ((3 * "*") + (10 * " ") + "RSU Commissioning Script Completed")
print (3 * "*")
print (64 * "*")