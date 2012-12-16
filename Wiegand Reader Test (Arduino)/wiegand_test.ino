// Definition of interrupt names
#include <avr/io.h>
// ISR interrupt service routine
#include <avr/interrupt.h>

// Count the number of bits received.
volatile int bitCount = 0;

// A 32-bit-long buffer into which the number is stored.
unsigned long keyNumber = 0;

// Data in pins for the Weigand protocol
int data0Pin = 2;     // INT0
int data1Pin = 3;     // INT1
int ledPin = 13;      // Light an LED to signify that a code has been outputted
int codeSize = 26;    // Assuming it's the Wiegand 26 protocol, there are 26 bits per number.

void setup()
{
  // Set the two data pins as inputs
  pinMode(data0Pin, INPUT);
  pinMode(data1Pin, INPUT);
  pinMode(ledPin, OUTPUT);
  
  // Attach interrupts to the two pins
  attachInterrupt(0, recv0, RISING);
  attachInterrupt(1, recv1, RISING);
  
  // Start a serial output so that we can read the numbers from the cards
  Serial.begin(9600);
  
  // Make sure the LED is out.
  digitalWrite(ledPin, LOW);
}

void recv0()
{
  // We've received a 0 bit.
  receive_bit(0);
}

void recv1()
{
  // We've received a 1 bit.
  receive_bit(1); 
}

void receive_bit(byte value)
{
  // Left shift the key number by one bit...
  keyNumber << 1;
  keyNumber |= value;
  bitCount++;
}

void loop()
{
  unsigned long buffer;
  // If we have the required number of bits, then we _should_ have
  // a complete key. Out it goes...
  if (bitCount == codeSize)
  {
    // Read in the current key and reset everything so that the interrupts can carry on in the background
    buffer = keyNumber;
    keyNumber = 0;
    bitCount = 0;

    // TODO: Strip leading and trailing parity bits from the buffer.
    
    // Light the LED
    digitalWrite(ledPin, HIGH);
    
    // Send the key number over the serial interface so that we can check it at the computer.
    // For now, it'll include the parity bits on both ends.
    Serial.println(buffer);
    // Wait 100ms so that the LED is visible as having pulsed.
    delay(100);
    // Turn off the LED
    digitalWrite(ledPin, LOW);    
  }
}
