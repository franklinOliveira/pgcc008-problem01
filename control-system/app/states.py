# coding: utf-8

import argparse
import sys
from datetime import datetime

sys.path.append('/home/pi/control-system/interfaces')
sys.path.append('/home/pi/control-system/sensors')
from simulatedEnvironment import SimulatedEnvironment
from dht22 import Dht22
from mqtt import Mqtt

class States:
    current_in_temp = 20
    current_in_hum = 0
    current_ex_temp = 0
    air_cond_command = 'O'
    min_temp = 20
    max_temp = 21

    mqtt = None

    def __init__(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-s", "--simulated", type=int, help="simulated environment")
        args = vars(ap.parse_args())

        self.mqtt = Mqtt()
        self.mqtt.connect()


        if args["simulated"] == 1:
            self.internalSensor = SimulatedEnvironment(None)
            self.internalSensor.start()
            self.airCondControl = self.internalSensor
            self.externalSensor = self.internalSensor
        elif args["simulated"] == 2:
            self.internalSensor = SimulatedEnvironment(Dht22(22))
            self.internalSensor.start()
            self.airCondControl = self.internalSensor
            self.externalSensor = Dht22(23)
            self.externalSensor.start()
        else:
            self.internalSensor = Dht22(22)
            self.internalSensor.start()
            self.airCondControl = SimulatedEnvironment(None)
            self.airCondControl.start()
            self.externalSensor = Dht22(23)
            self.externalSensor.start()


        print("[DEVICE] Control System started")

    def readSensors(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        newRange = False

        newData = self.mqtt.dataSubscribed[0]
        if newData != self.min_temp:
            self.min_temp = newData
            newRange = True

        newData = self.mqtt.dataSubscribed[1]
        if newData != self.max_temp:
            self.max_temp = newData
            newRange = True

        if newRange is True:
            print("[DEVICE at", current_time+"] Internal temperature range: "+str(self.min_temp)+" to "+str(self.max_temp)+"C")

        next_in_temp = self.internalSensor.read("IN_TEMP")
        if next_in_temp != self.current_in_temp:
            self.current_in_temp = next_in_temp
            self.mqtt.publish("pgcc008/problem01/sensor/internal/temperature", self.current_in_temp)
            print("[DEVICE at", current_time+"] Internal temperature: "+str(self.current_in_temp)+"C")

        next_in_hum = self.internalSensor.read("IN_HUM")
        if next_in_hum != self.current_in_hum:
            self.current_in_hum = next_in_hum
            self.mqtt.publish("pgcc008/problem01/sensor/internal/humidity", self.current_in_hum)
            print("[DEVICE at", current_time+"] Internal humidity: "+str(self.current_in_hum)+"%")

        next_ex_temp = self.externalSensor.read("EX_TEMP")
        if next_ex_temp != self.current_ex_temp:
            self.current_ex_temp = next_ex_temp
            self.mqtt.publish("pgcc008/problem01/sensor/external/temperature", self.current_ex_temp)
            print("[DEVICE at", current_time+"] External temperature: "+str(self.current_ex_temp)+"C")

    def sendAirCondCommand(self, command):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        self.air_cond_command = command
        self.airCondControl.write(self.air_cond_command)
        self.mqtt.publish("pgcc008/problem01/sensor/internal/air_cond_state", self.air_cond_command)

        if self.air_cond_command == 'O':
            print("[DEVICE at", current_time+"] Air conditioning state: off")
        elif self.air_cond_command == 'H':
            print("[DEVICE at", current_time+"] Air conditioning state: heating")
        elif self.air_cond_command == 'C':
            print("[DEVICE at", current_time+"] Air conditioning state: cooling")

    def stop(self):
        self.sendAirCondCommand('O')
        self.internalSensor.stopRead()
        self.externalSensor.stopRead()
        self.airCondControl.stopRead()
        self.mqtt.disconnect()
