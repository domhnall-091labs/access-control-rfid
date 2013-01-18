#!/usr/bin/env bash
# Auto configuration script to set up DS1307-based RTC (real-time clock) on a
# Raspberry Pi. 

# The DS1307 has a hard-coded I2C address of 0x68 (104 decimal?), but the
# two different Pi boards expose two different I2C buses on the P1 connector
# where all the GPIO lives, so the script has to auto-detect which bus to use.
# It also (ideally) needs to detect if there is an RTC on the bus before it
# attempts to use it.

# Ensure script only run as root!
if [ "$(id -u)" != "0" ]; 
then
  echo "This script must be run as root" 1>&2
	exit 1
fi

# I'm sure this can be done better with awk or something, but...
pi_revision_number=$(cat /proc/cpuinfo | grep ^Revision | cut -f3 -d" " | cut -c7)

# This ensures that the revision number is in fact set.
if [[ -z $pi_revision_number ]]
then
	echo "Failed to detect revision number of Raspberry Pi board. Exiting."
	exit 1
fi

# Select board version and I2C bus number based on hardware revision number
# According to http://www.raspberrypi.org/archives/1929 the last digit of the
# Revision number in /proc/cpuinfo can tell you what's what:
#
# Model and revision										                  Code(s)
# Model B Revision 1.0									                  2
# Model B Revision 1.0 + ECN0001 (no fuses, D14 removed)	3
# Model B Revision 2.0										                4, 5, 6

if (( pi_revision_number < 4 ))
then
	board_version=1
	i2c_bus=0
else
	board_version=2
	i2c_bus=1
fi

# TODO: Add automatic RTC detection code using i2cdetect (or something) here.
# This would be to ensure that the RTC is actually present before trying to
# use it...
echo "Revision $board_version.0 Pi found. Using I2C #$i2c_bus..."
echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-$i2c_bus/new_device
