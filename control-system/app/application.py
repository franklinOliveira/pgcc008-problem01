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
GPIO.setup(F_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def main():
    while True:
        states.readSensors()

        if states.current_in_temp >= states.min_temp and states.current_in_temp <= states.max_temp:
            states.off()
        elif states.current_in_temp < states.min_temp:
            states.heating()
        elif states.current_in_temp > states.max_temp:
            states.cooling()

        states.controlAirCond()

        print(states.current_in_temp)
        if GPIO.input(F_button_pin) == GPIO.HIGH:
            break
        time.sleep(1)

if __name__ == "__main__":
    main()
    states.off()
