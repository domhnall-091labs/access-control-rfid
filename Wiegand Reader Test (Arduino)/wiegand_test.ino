// Definition of interrupt names
#include <avr/io.h>
// ISR interrupt service routine
#include <avr/interrupt.h>

// Count the number of bits received.
volatile int bitCount = 0;

// A 32-bit-long keyBuffer into which the number is stored.
unsigned long keyBuffer = 0;

// Data in pins for the Weigand protocol
int data0Pin = 2; // INT0
int data1Pin = 3; // INT1
int ledPin = 13; // Light an LED to signify that a code has been outputted
int codeSize = 26; // Assuming it's the Wiegand 26 protocol, there are 26 bits per number.

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
  // Left shift the number (effectively multiplying by 2)
  keyBuffer = keyBuffer << 1;
  // Increment the bit count
  bitCount++;
}

void recv1()
{
  // We've received a 1 bit.
  // Left shift the number (effectively multiplying by 2)
  keyBuffer = keyBuffer << 1;
  // Add the 1 (not necessary for the zeroes)
  keyBuffer += 1;
  // Increment the bit count
  bitCount++;
}

void loop()
{
  // If we have the required number of bits, then we _should_ have
  // a complete key. Out it goes...
  if (bitCount == codeSize)
  {
    // Read in the current key and reset everything so that the interrupts can
    // carry on in the background.
    bitCount = 0;

    // Strip leading and trailing parity bits from the keyBuffer. For now, we're ignoring them.
    keyBuffer = keyBuffer >> 1;
    keyBuffer &= 0xFFFFFF;
    
    // Light the LED
    digitalWrite(ledPin, HIGH);
        
    Serial.print("Got key: ");
    Serial.println(keyBuffer);

    // Wait 100ms so that the LED is visible as having pulsed.
    delay(100);

    // Turn off the LED
    digitalWrite(ledPin, LOW);
    
    // Clear the buffer for the next iteration.
    keyBuffer = 0;
  }
}
