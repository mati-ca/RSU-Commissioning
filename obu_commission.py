# python3 commission.py 192.168.0.54 Sdsm On - CV2X Radios ON
# python3 commission.py 192.168.0.54 Sdsm Off - CV2X Radios OFF
# python3 commission.py 192.168.0.54 Psm - On - CV2X Radios ON
# python3 commission.py 192.168.0.54 Psm - Off - CV2X Radios OFF

#from curses.ascii import isdigit
import isdigit # pip3 install isdigit
import paramiko # pip3 install paramiko
import sys
import os
import getpass

def do_on_obu(arg):
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
print ((3 * "*") + (10 * " ") + "Welcome to OBU Commissioning Script")
print (3 * "*")
print (64 * "*")


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())



def login():
	#user = input('Enter Device username: ')
	#print(user)
	user = 'root'
	pass_sel = input("Do you want to enter password manualy:: y/n " )
	if (pass_sel == 'y'):
		pwd = getpass.getpass('Enter current password: ')
	else: 
		pwd = getCredentials()
	print("Current Used IP Address: ",sys.argv[1] )
	ip_add_sel = input('Do You Want to Change the IP Address: y/n ')
	if ip_add_sel == 'y':
		new_ip_add = input('Type NEW IP Address, (Ex 192.168.0.55) ')
		hostname=new_ip_add
	else: 
		hostname=sys.argv[1]
	client.connect(hostname, username=user, password=pwd,timeout=10.0 )

while True:
	try:
		login()
		break
	except (paramiko.AuthenticationException):
		print("Something went wrong - Check Crudential and Try Again")
	except TimeoutError:
		print("Connection Time OUT - Check Again the IP Address ")
	#finally:
	#	print("The 'try except' is finished") 

do_on_obu("muci cff set sensorAdapters.udpAdapter.enable true")
do_on_obu("muci cff set sensorAdapters.udpAdapter.port 12321")
do_on_obu("muci saf set native.sensorSharing.enable true")
do_on_obu("muci saf set native.sensorSharing.excludeV2xSendingObjects false")

if "sdsm" in sys.argv[2].lower():
	do_on_obu("muci its set sdsmTx.enable true")
	do_on_obu("muci its set sdsmTx.radioInterface 'default'")
	do_on_obu("muci saf set native.sensorSharing.mode Sdsm")

if "psm" in sys.argv[2].lower():
	do_on_obu("muci saf set native.sensorSharing.mode Psm")

if "on" in sys.argv[3].lower():
	do_on_obu("muci its set radio.qc9150.enable true")

if "off" in sys.argv[3].lower():
	do_on_obu("muci its set radio.qc9150.enable false")


# only change the camera position if the navigation is valid
nav_is_valid = do_on_obu("muci stat navigation.isValid")
if "true" in nav_is_valid:
	print("navigation is valid ")
	# # the latitude from navigation stats (it is an int)
	# lat = do_on_obu("muci stat navigation.latitude").split(' ')[-2]
	# lat = lat[:-7] + "." + lat[-7:]
	# # set latitude in decimal
	# do_on_obu("muci cff set sensorAdapters.camera.position.lat " + lat)
	# # read back the latitude to check that the set worked right
	# do_on_obu("muci cff get sensorAdapters.camera.position.lat")
	# # the logitude from navigation stats (it is an int)
	# lon = do_on_obu("muci stat navigation.longitude").split(' ')[-2]
	# lon = lon[:-7] + "." + lon[-7:]
	# # set logitude in decimal
	# do_on_obu("muci cff set sensorAdapters.camera.position.lon " + lon)
	# # read back the longitude to check that the set worked right
	# do_on_obu("muci cff get sensorAdapters.camera.position.lon")
else:
	print("navigation isn't valid ")

do_on_obu("muci its set capture.enable true")
do_on_obu("muci its set capture.address 192.168.0.188")

do_on_obu("unplugged-rt-restart.sh")

#check firewall
found_rule = False
index = 0
while(True):
	result = do_on_obu("uci get firewall.@rule[" + str(index) + "]")
	if "rule" in result:
		dest_port = do_on_obu("uci get firewall.@rule[" + str(index) + "].dest_port")
		if dest_port.isdigit() and int(dest_port) == 12321:
			proto = do_on_obu("uci get firewall.@rule[" + str(index) + "].proto")
			src = do_on_obu("uci get firewall.@rule[" + str(index) + "].src")
			if "udp" in proto and "wan" in src:
				found_rule = True
				break
	else:
		break
	index += 1

# add the rule if it isn't found
if not found_rule:
	do_on_obu("uci add firewall rule")
	do_on_obu("uci set firewall.@rule[-1].name='UDP Adapter'")
	do_on_obu("uci set firewall.@rule[-1].src='wan'")
	do_on_obu("uci set firewall.@rule[-1].proto='udp'")
	do_on_obu("uci set firewall.@rule[-1].target='ACCEPT'")
	do_on_obu("uci set firewall.@rule[-1].dest_port='12321'")
	do_on_obu("uci commit")
	do_on_obu("/etc/init.d/firewall restart")

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

def PasswordValid():
	while True:
		while True:
			new_pwd = getpass.getpass('Enter NEW password: ')
			if IsPasswordValid(new_pwd):
				break
			print("Enter Valid Password - Length 5-15, 1 LowerCase, 1 UpperCase, One Special")
		retype_pwd = getpass.getpass('Retype NEW password: ')
		if retype_pwd == new_pwd:
			return new_pwd
		print("Hoops Youe Retyped Wrong Password Try Again")


new_pass = PasswordValid()
do_on_obu("echo -e '" + new_pass + "\n" + new_pass + "' | passwd -q")
print (64 * "*")
print (3 * "*")
print ((3 * "*") + (10 * " ") + "OBU Commissioning Script Completed")
print (3 * "*")
print (64 * "*")