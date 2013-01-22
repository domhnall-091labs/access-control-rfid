#!/usr/bin/env python
import os, sys, commands, re

DS1307_I2C_ID = 68	# 0x68
number_regex = re.compile('[0-9]+')

def enumerate_i2c_buses():
	# Get a list of the names of the i2c buses
	shell_command = 'i2cdetect -l'
	result_code, results = commands.getstatusoutput(shell_command)
	
	if result_code != 0:
		print >> sys.stderr, "Couldn't execute '%s'" % shell_command
		return []
	
	# Need to return the first field off each line. Each line is tab delimited.
	return [r.split('\t')[0] for r in results.split('\n')]

def scan_i2c_bus(id):
	# Use i2cdetect to detect any devices that are on the bus
	shell_command = 'i2cdetect -y %d' % id

	result_code, results = commands.getstatusoutput(shell_command)

	if result_code != 0:
		print >> sys.stderr, "Couldn't execute '%s'" % shell_command
		return []

	# Ignore the first line, it's just column headers...
	results = results.split('\n')[1:]

	i2c_devices = []

	for row in results:
		row_ids = [int(item) for item in number_regex.findall(row)]
		i2c_devices += row_ids
	
	# Make sure the list returned is unique.
	return list(set(i2c_devices))

if __name__ == '__main__':
	# Make sure this program only runs as root.
	if not os.geteuid()==0:
		sys.exit("\nOnly root can run this script\n")	

	# Get the i2c bus IDs and extract the numerical portions from those.
	i2c_buses = [int(bus_id[-1]) for bus_id in enumerate_i2c_buses()]

	for bus in i2c_buses:
		devices = scan_i2c_bus(bus)

		if DS1307_I2C_ID in devices:
			print >> sys.stderr, "DS1307 found on I2C bus #%d" % bus
			print bus
			# TODO: 
			sys.exit(0)

	# If we get to here, then the search failed.
	sys.exit(1)
