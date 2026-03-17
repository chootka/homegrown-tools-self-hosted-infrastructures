int POT_X = A0;
int POT_Y = A1;
int BUTTON_PIN = 2;

void setup() {
  Serial.begin(9600);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  // Check if the button is pressed
  if (digitalRead(BUTTON_PIN) == LOW) {
    Serial.println("CLEAR");
    delay(300);  // Simple debounce
    return;
  }

  int x = analogRead(POT_X);
  int y = analogRead(POT_Y);

  Serial.print(x);
  Serial.print(",");
  Serial.println(y);

  delay(20);
}
