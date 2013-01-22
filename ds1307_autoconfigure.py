#!/usr/bin/env python
import os, sys, re, datetime
from exceptions import OSError  		# Not sure if this is the right way to go.

DEVICE_I2C_ID = 68						# Actually 0x68, but i2cdetect speaks hex
DEVICE_NAME = 'ds1307'					
number_regex = re.compile('[0-9]+')		# Generic regex to extract numbers

def shell_execute(command):
	# Run a shell command and raise an exception if it doesn't work.
	import commands

	result_code, output = commands.getstatusoutput(command)

	# Make sure that the command actually ran successfully...
	if result_code != 0:
		raise RunTimeException("Failed to execute command '%s' - code %s, message %r" % (command, result_code, output))
	else:
		return output

def enumerate_i2c_buses():
	# Get a list of the names of all the i2c buses known to i2cdetect.
	shell_command = 'i2cdetect -l'
	try:
		return [row.split('\t')[0] for row in shell_execute(shell_command).split('\n')]
	except OSError:
		return []

def scan_i2c_bus(id):
	# Use i2cdetect to detect any devices that are on the specified bus.
	shell_command = 'i2cdetect -y %d' % id
	i2c_devices = []

	try:
		results = shell_execute(shell_command).split('\n')[1:]
	except OSError:
		return []

	for row in results:
		i2c_devices += [int(device_address) for device_address in number_regex.findall(row)]

	# Make sure the list returned is unique.
	return list(set(i2c_devices))

if __name__ == '__main__':
	# Make sure this program only runs as root.
	if not os.geteuid()==0:
		sys.exit("\nOnly root can run this script\n")	

	# Get the i2c bus IDs and extract the numerical portions from those.
	i2c_buses = enumerate_i2c_buses()
	i2c_bus_ids = [int(bus[-1]) for bus in i2c_buses]

	device_found = False
	for bus in i2c_buses:
		bus_id = int(bus.split('-')[-1])
		device_addresses = scan_i2c_bus(bus_id)

		if DEVICE_I2C_ID in device_addresses:
			print "%s found on I2C bus %s. Configuring..." % (DEVICE_NAME, bus)
			device_found = True

			# Register RTC as hardware clock.
			shell_command = "echo %s 0x%d > /sys/class/i2c-adapter/%s/new_device" % (DEVICE_NAME, DEVICE_I2C_ID, bus)
			try:
				shell_execute(shell_command)
				print "Done."
				sys.exit(0)
			except OSError, e:
				sys.exit("\nFailed: %s\n" % e.message) 

	if not device_found:
		sys.exit("\nFailed to find RTC module on I2C bus. Sorry.\n")

	# If we get to there, we have a clock. Let's check if we can read it...
	try:
		output = shell_execute('hwclock -r').split("  ")[0]	# need to lose the error factor...
		# Tue 22 Jan 2013 13:36:34 GMT  -0.073809 seconds
		rtc_time = datetime.datetime.strptime("%a %d %b %Y %H:%M:%S %Z")
		print "RTC    time is: %r" % rtc_time
	except OSError, e:
		sys.exit("\nFailed to read RTC. Got error: %s\n" % e.message)
