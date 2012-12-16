What's this?
============
This is basically a test harness, usign an [Arduino](http://www.arduino.cc),
whose purpose is to test that we can reliably read data from RFID readers using the Wiegand-26 (and related) protocols.

It's just to test the logic of the decoding and experiment with different 
techniques, and to ultimately form the "bridge" between the Pi and the RFID 
reader, where the Arduino (or similar) does the timing-critical stuff. A small 
ATTiny should do the trick nicely. 
