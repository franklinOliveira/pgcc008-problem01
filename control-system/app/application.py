from states import States
import time
import RPi.GPIO as GPIO
import os.path
import csv
from datetime import datetime


#Control system states
states = States()

#Finish button (3V3)
F_button_pin = 13

#Door simulation (3V3)
D_button_pin = 18

#Ignore warning
GPIO.setwarnings(False)
#Use physical pin numbering
GPIO.setmode(GPIO.BOARD)
#Set pins to be an input pin and set initial value to be pulled low (off)
GPIO.setup(F_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(D_button_pin, GPIO.OUT)

#Starts with door closed
GPIO.output(D_button_pin, GPIO.HIGH)

def main():
    #Loads simulation file and define a automatic interaction routine
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

    #Starts on off state
    currentState = "off"
    while True:
        #Checks if automatic routine is enabled
        if len(simulation_data) > 0:
            now = datetime.now()

            #Checks if is time to open/close the door
            if simulation_data[0] == now.strftime("%H:%M:%S"):
                print("[DEVICE at", now.strftime("%H:%M:%S")+"] Door state changed")
                GPIO.output(D_button_pin, GPIO.LOW)
                time.sleep(0.3)
                GPIO.output(D_button_pin, GPIO.HIGH)
                del(simulation_data[0])

        previousState = currentState

        #Reads all sensors
        states.readSensors()

        #Checks control state
        if states.current_in_temp >= states.min_temp and states.current_in_temp <= states.max_temp:
            currentState = "off"
        elif states.current_in_temp < states.min_temp:
            currentState = "heating"
        elif states.current_in_temp > states.max_temp:
            currentState = "cooling"

        #Sends control state to air conditioner
        states.sendAirCondCommand(currentState)

        if GPIO.input(F_button_pin) == GPIO.LOW:
            break
        time.sleep(0.5)

if __name__ == "__main__":
    main()
    states.stop()
