#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const int TrigPin = 12; 
const int EchoPin = 11; 
const int BuzzerPin = 10; 
const int LedPin = 8; 

Servo myServo; 


LiquidCrystal_I2C lcd(0x27, 16, 2);  

void setup() {
  Serial.begin(9600);
  pinMode(TrigPin, OUTPUT);
  pinMode(EchoPin, INPUT);
  pinMode(BuzzerPin, OUTPUT);
  pinMode(LedPin, OUTPUT);

  myServo.attach(9); 
  
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0); 
  lcd.print("Distance:"); 
}

void loop() {
  long duration, distance_cm;
  
  digitalWrite(TrigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(TrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(TrigPin, LOW);
  
  duration = pulseIn(EchoPin, HIGH);
  
  distance_cm = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.print(distance_cm);
  Serial.println(" cm");

  
  lcd.setCursor(10, 0); 
  lcd.print(distance_cm);
  lcd.print(" cm  ");
  
  digitalWrite(LedPin, HIGH);

  if (distance_cm < 6) {
    tone(BuzzerPin, 1000, 1000);
    
    
    lcd.setCursor(0, 1); 
    lcd.print("Danger!       ");
    
    
    
for (int i = 0; i < 2; i++) {
      myServo.write(90); 
      delay(500); 
      myServo.write(0); 
      delay(500); 
    }
  } else {
    
    noTone(BuzzerPin);
    myServo.write(0); 
    
    lcd.setCursor(0, 1);
    lcd.print("                "); 
  
    digitalWrite(LedPin, LOW);
  }

  delay(500); 
}
