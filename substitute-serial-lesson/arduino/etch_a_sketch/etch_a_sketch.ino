int POT_X = A0;
int POT_Y = A1;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int x = analogRead(POT_X);
  int y = analogRead(POT_Y);

  // Send both values separated by a comma
  Serial.print(x);
  Serial.print(",");
  Serial.println(y);

  delay(20);
}
