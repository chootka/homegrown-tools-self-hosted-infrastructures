// Growing Circle — receives a potentiometer value from Arduino over serial
// and uses it to control the size of a circle on screen.

import processing.serial.*;

Serial port;
int circleSize;

void setup() {
  size(600, 600);

  // Print available serial ports to the console.
  // Find your Arduino in the list and change the index below.
  printArray(Serial.list());

  // Change the index [0] to match your Arduino's position in the list above.
  port = new Serial(this, Serial.list()[3], 9600);

  // Read incoming data one line at a time (matching Arduino's Serial.println).
  port.bufferUntil('\n');
}

void draw() {
  background(30);

  fill(255, 150, 0);
  noStroke();
  ellipse(width / 2, height / 2, circleSize, circleSize);
}

// Runs automatically every time a complete line arrives from Arduino.
void serialEvent(Serial p) {
  String s = p.readStringUntil('\n');
  if (s == null) return;

  int v = int(trim(s));
  circleSize = int(map(v, 0, 1023, 10, 500));
}
