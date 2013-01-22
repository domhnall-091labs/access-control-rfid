#!/usr/bin/env python
import os, sys, commands, re  # 'commands' requires python 2.7

DS1307_I2C_ID = 68  # 0x68
number_regex = re.compile('[0-9]+')

def enumerate_i2c_buses:
	# Get a list of the names of the i2c buses
	shell_command = 'i2cdetect -l | cut -f1'
	return commands.getoutput(shell_command).split('\n')

def scan_i2c_bus(id):
	# Use i2cdetect to detect any devices that are on the bus
	shell_command = 'i2cdetect -y %d' % id

	# Ignore the first line, it's just column headers...
	results = commands.getoutput(shell_command).split('\n')[1:]

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
	i2c_buses = enumerate_i2c_buses()
	i2c_bus_numbers = [int(bus_id[-1]) for bus_id in i2c_buses]

	for bus in i2c_bus_numbers:
		devices = scan_i2c_bus(bus)

		if DS1307_I2C_ID in devices:
			print >> sys.stderr "DS1307 found on I2C bus #%d" % 
			print bus
			sys.exit(0)

	# If we get to here, then the search failed.
	sys.exit(1)
