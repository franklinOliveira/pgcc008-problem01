from states import States
import time
import RPi.GPIO as GPIO
import os.path
import csv
from datetime import datetime


states = States()

#Finish button (3V3)
F_button_pin = 13
#Door button (3V3)
D_button_pin = 18

#Ignore warning
GPIO.setwarnings(False)
#Use physical pin numbering
GPIO.setmode(GPIO.BOARD)
#Set pins to be an input pin and set initial value to be pulled low (off)
GPIO.setup(F_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(D_button_pin, GPIO.OUT)

GPIO.output(D_button_pin, GPIO.HIGH)

def main():
    path = "simulation.csv"
    simulation_data = list()

    if os.path.isfile(path):
        with open(path, 'r') as file:
            file_reader = csv.reader(file)
            firstRead = True

            for row in file_reader:
                if firstRead is True:
                    firstRead = False
                else:
                    sample = row[0]
                    simulation_data.append(sample)

    currentState = 'O'
    while True:
        if len(simulation_data) > 0:
            now = datetime.now()

            if simulation_data[0] == now.strftime("%H:%M:%S"):
                print("[DEVICE at", now.strftime("%H:%M:%S")+"] Door state changed")
                GPIO.output(D_button_pin, GPIO.LOW)
                time.sleep(0.3)
                GPIO.output(D_button_pin, GPIO.HIGH)
                del(simulation_data[0])

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
