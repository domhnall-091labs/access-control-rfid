#!/usr/bin/env python
import os, sys, datetime
from exceptions import OSError			# Not sure if this is the right way to go.

DEVICE_I2C_ID = 0x68					# i2cdetect speaks hex
DEVICE_NAME = 'ds1307'					
TIME_TOLERANCE = 2						# How close the two clocks have to be for updating to be skipped.

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
	i2c_devices = {}

	try:
		results = shell_execute(shell_command).split('\n')[1:]
	except OSError:
		return []

	for row in results:
		row_offset = int(row[:2], 16)	# Addresses are all in hex...
		if row_offset == 0:
			row_index = 3
		else:
			row_index = 0

		row_data = [i.strip() for i in row[4:].strip().split(" ")]
		for value in row_data:
			address = hex(row_offset + row_index)
			if value != "--":
				i2c_devices[address] = value
			row_index += 1
	
	return i2c_devices

if __name__ == '__main__':
	# Make sure this program only runs as root.
	if not os.geteuid()==0:
		sys.exit("\nOnly root can run this script\n")	

	# TODO: Check if system was able to set clock via NTP; if so update the RTC
	# with the newly fetched (and accurate) time, otherwise use the RTC to set
	# the clock.

	# Get the i2c bus IDs and extract the numerical portions from those.
	i2c_buses = enumerate_i2c_buses()
	i2c_bus_ids = [int(bus[-1]) for bus in i2c_buses]

	device_found = False
	for bus in i2c_buses:
		bus_id = int(bus.split('-')[-1])
		device_addresses = scan_i2c_bus(bus_id)

		# Check if there's a device at the address specified.
		device_id_string = "%#x" % DEVICE_I2C_ID
		if device_id_string in device_addresses.keys():
			device_found = True

			# Need to check if the device is in use or not...
			if device_addresses[device_id_string] == "UU":
				# Device is in use...
				print "Device at address %#x already in use, skipping configuration phase." % DEVICE_I2C_ID
			else:
				print "%s found on I2C bus %s. Configuring..." % (DEVICE_NAME, bus)

				# Register RTC as hardware clock.
				shell_command = "echo %s 0x%d > /sys/class/i2c-adapter/%s/new_device" % (DEVICE_NAME, DEVICE_I2C_ID, bus)
				try:
					shell_execute(shell_command)
					print "Hardware RTC registered successfully."
				except OSError, e:
					sys.exit("\nFailed: %s\n" % e.message) 

	if not device_found:
		sys.exit("\nFailed to find RTC module on I2C bus. Sorry.\n")

	# If we get to there, we have a clock. Let's check if we can read it...
	try:
		rtc_output = shell_execute('hwclock -r').split("  ")[0]	# need to lose the error factor...
		# Tue 22 Jan 2013 13:36:34 GMT  -0.073809 seconds
		rtc_output = output.split("  ")[0]	# This removes the "... seconds" bit on the end
		rtc_time = datetime.datetime.strptime(rtc_output, "%a %d %b %Y %H:%M:%S %Z")
		print "RTC    time is: %s" % rtc_time
	except OSError, e:
		sys.exit("\nFailed to read RTC. Got error: %s\n" % e.message)

	# Now get the time the system thinks it is...
	system_time = datetime.datetime.now()
	system_time.millis = 0
	print "System time is: %s" % system_time

	if rtc_time > system_time:
		delta = rtc_time - system_time
	else:
		delta = system_time - rtc_time

	print "Difference is %d seconds" % delta.seconds

	# Update the system clock if needs be. Assume the hardware RTC knows best.
	if abs(delta.seconds) > TIME_TOLERANCE:
		try:
			shell_execute("hwclock --hctosys")
		except OSError, e:
			sys.exit("\nFailed to update system clock. Reason: '%s'\n" % e.message
	else:
		print "Clock already sufficiently accurate, not updating"
