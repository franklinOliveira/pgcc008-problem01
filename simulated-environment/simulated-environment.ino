#include <ESP8266WiFi.h>
#include <SoftwareSerial.h>

#define heating_led D0
#define door_state_led D3
#define cooling_led D4
#define door_mod D5
SoftwareSerial ControlSystem(D2, D1); //rx, tx

//Off ('O'), Heating ('H') or Cooling ('C')
char air_cond_command = 'O';
//Open (0) or Closed (1)
bool door_state = 1;
//Stopped (0), Heating (> 0) or Cooling (< 0)
float temp_change_rate = 0.0;

float current_temp = 20.0;

void setup() {
  ControlSystem.begin(9600);
  Serial.begin(9600);
  pinMode(door_mod, INPUT_PULLUP);
  pinMode(heating_led, OUTPUT);
  pinMode(door_state_led, OUTPUT);
  pinMode(cooling_led, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(door_mod), doorModDetectISR, RISING);  

}

void loop() {
  checkAirCond();
  calculeCurrentTemp();
  controlLeds();
  debugDisplay();
  ControlSystem.print(current_temp);
  delay(1000);
}

ICACHE_RAM_ATTR void doorModDetectISR() {
  if (door_state == 0)
    door_state = 1;
  else
    door_state = 0;
}

void checkAirCond(){
  if(ControlSystem.available() > 0){
    char incomingByte = ControlSystem.read();
    
    if(incomingByte == 'O' || incomingByte == 'H' || incomingByte == 'C')
      air_cond_command = incomingByte;
  }
  
}

void calculeCurrentTemp(){
  if(air_cond_command == 'O')
    temp_change_rate = 0.0;
  else if(air_cond_command == 'H')
    temp_change_rate = 1.0;
  else if(air_cond_command == 'C')
    temp_change_rate = -1.0;

  if(door_state == 0 && current_temp < 25.0)
    temp_change_rate+=0.1;
  else if(door_state == 0 && current_temp > 25.0)
    temp_change_rate-=0.1;
   
  current_temp+=(temp_change_rate/60.0);
}

void debugDisplay(){
  Serial.print("Door situation: ");
  if(door_state == 0)
    Serial.print("open | ");
  else
    Serial.print("closed | ");
    
  Serial.print("Air conditioning situation: ");
  if(air_cond_command == 'O')
    Serial.print("off | ");
  else if(air_cond_command == 'H')
    Serial.print("heating | ");
  else if(air_cond_command == 'C')
    Serial.print("cooling | ");

  Serial.print("Temperature change rate: ");
  Serial.print(temp_change_rate);
  Serial.print("ºC/min | ");

  Serial.print("Current temperature: ");
  Serial.print(current_temp);
  Serial.println("ºC");
}

void controlLeds(){
  if(door_state == 0)
    digitalWrite(door_state_led, HIGH);
  else
    digitalWrite(door_state_led, LOW);

  if(air_cond_command == 'O'){
    digitalWrite(heating_led, LOW);
    digitalWrite(cooling_led, LOW);
  }
  else if(air_cond_command == 'H'){
    digitalWrite(heating_led, HIGH);
    digitalWrite(cooling_led, LOW);
  }
  else if(air_cond_command == 'C'){
    digitalWrite(heating_led, LOW);
    digitalWrite(cooling_led, HIGH);
  }
}
