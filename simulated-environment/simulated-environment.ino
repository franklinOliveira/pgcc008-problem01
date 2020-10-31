#include <ESP8266WiFi.h>
#include <SoftwareSerial.h>

#define heating_led D0
#define door_state_led D3
#define cooling_led D4
#define door_mod D5
SoftwareSerial ControlSystem(D2, D1); //rx, tx

//Sets the heating/cooling rate of the air conditioner
float air_cond_interaction = 0.0;
//Open (0) or Closed (1)
bool door_state = 1;
//Stopped (0), Heating (> 0) or Cooling (< 0)
float temp_change_rate = 0.0;

//Current temperature inside the safe box
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

//Simulated environment routine
void loop() {
  checkAirCond();
  calculeCurrentTemp();
  controlLeds();
  ControlSystem.print(current_temp);
  delay(1000);
}

//Captures the opening of the door through the button state transition
ICACHE_RAM_ATTR void doorModDetectISR() {
  if (door_state == 0)
    door_state = 1;
  else
    door_state = 0;
}

//Takes the heating/cooling rate of the control system
void checkAirCond(){
  if(ControlSystem.available() > 0)
    air_cond_interaction = ControlSystem.readString().toFloat();

}

//Calculates the current temperatur
void calculeCurrentTemp(){
  float previous_temp = current_temp;
  
  temp_change_rate = air_cond_interaction;
  if(door_state == 0 && current_temp < 25.0)
    temp_change_rate+=0.1;
  else if(door_state == 0 && current_temp > 25.0)
    temp_change_rate-=0.1;
   
  current_temp+=(temp_change_rate/60.0);
}

//Controls the activity indicator leds of the simulated environment
void controlLeds(){
  if(door_state == 0)
    digitalWrite(door_state_led, HIGH);
  else
    digitalWrite(door_state_led, LOW);

  if(air_cond_interaction == 0.0){
    digitalWrite(heating_led, LOW);
    digitalWrite(cooling_led, LOW);
  }
  else if(air_cond_interaction > 0.0){
    digitalWrite(heating_led, HIGH);
    digitalWrite(cooling_led, LOW);
  }
  else if(air_cond_interaction < 0.0){
    digitalWrite(heating_led, LOW);
    digitalWrite(cooling_led, HIGH);
  }
}
