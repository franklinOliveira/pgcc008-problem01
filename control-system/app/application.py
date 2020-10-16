from states import States
import time
import RPi.GPIO as GPIO

states = States()

#Finish button (3V3)
F_button_pin = 13

#Ignore warning
GPIO.setwarnings(False)
#Use physical pin numbering
GPIO.setmode(GPIO.BOARD)
#Set pins to be an input pin and set initial value to be pulled low (off)
GPIO.setup(F_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    currentState = 'O'
    while True:
        previousState = currentState
        states.readSensors()

        if states.current_in_temp >= states.min_temp and states.current_in_temp <= states.max_temp:
            currentState = 'O'
        elif states.current_in_temp < states.min_temp:
            currentState = 'H'
        elif states.current_in_temp > states.max_temp:
            currentState = 'C'

        if currentState != previousState:
            states.sendAirCondCommand(currentState)

        if GPIO.input(F_button_pin) == GPIO.LOW:
            break
        time.sleep(0.5)

if __name__ == "__main__":
    main()
    states.stop()
