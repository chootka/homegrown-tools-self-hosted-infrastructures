int POT_PIN = A0;
int POT_PIN2 = A1;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int potValue = analogRead(POT_PIN);
  int potValue2 = analogRead(POT_PIN2);

  Serial.print(potValue);
  Serial.print(",");
  Serial.println(potValue2);
  delay(50);
}
