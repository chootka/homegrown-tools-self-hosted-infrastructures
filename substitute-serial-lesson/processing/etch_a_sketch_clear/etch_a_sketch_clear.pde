// Etch A Sketch with Clear Button — press a button to erase the canvas.

import processing.serial.*;

Serial port;
float penX, penY;

void setup() {
  size(800, 800);
  background(255);

  printArray(Serial.list());

  // Change the index [0] to match your Arduino's position in the list.
  port = new Serial(this, Serial.list()[3], 9600);
  port.bufferUntil('\n');
}

void draw() {
}

void serialEvent(Serial p) {
  String s = p.readStringUntil('\n');
  if (s == null) return;
  s = trim(s);

  // If the button was pressed, Arduino sends "CLEAR".
  if (s.equals("CLEAR")) {
    background(255);
    return;
  }

  // Otherwise it's a normal "x,y" pair.
  String[] values = split(s, ',');
  if (values.length < 2) return;

  float newX = map(int(values[0]), 0, 1023, 0, width);
  float newY = map(int(values[1]), 0, 1023, 0, height);

  stroke(0);
  strokeWeight(3);
  line(penX, penY, newX, newY);

  penX = newX;
  penY = newY;
}
