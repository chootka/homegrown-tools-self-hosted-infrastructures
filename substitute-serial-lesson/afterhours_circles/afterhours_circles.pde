// Growing Circle — receives a potentiometer value from Arduino over serial
// and uses it to control the size of a circle on screen.

import processing.sound.*;
import processing.serial.*;

SawOsc saw;

Serial port;
int val1;
int val2;

void setup() {
  size(600, 600);

  // Print available serial ports to the console.
  // Find your Arduino in the list and change the index below.
  printArray(Serial.list());
  
  saw = new SawOsc(this);
  saw.play();
  saw.amp(.7);

  // Change the index [0] to match your Arduino's position in the list above.
  port = new Serial(this, Serial.list()[3], 9600);

  // Read incoming data one line at a time (matching Arduino's Serial.println).
  port.bufferUntil('\n');
}

void draw() {
  background(val2);
  
  saw.freq(val2);

  fill(val1, val2, 0);
  noStroke();
  ellipse(width / 2, height / 2, val1*2, val1*2);
}

// Runs automatically every time a complete line arrives from Arduino.
void serialEvent(Serial p) {
  String s = p.readStringUntil('\n');
  if (s == null) return;
  
  // s is going to look like, for ex: "211,45"
  // we want to transform this into usable numbers
  // split(s, ',') = [211, 45]
  
  String[] values = split(s, ',');
  
  if (values.length < 2) return;
  
  int v1 = int(trim(values[0]));
  int v2 = int(trim(values[1]));
  
  val1 = int(map(v1, 0, 1023, 10, 255));
  val2 = int(map(v2, 0, 1023, 0, 127));

  // int v = int(trim(s));
  // circleSize = int(map(v, 0, 1023, 10, 255));
}
