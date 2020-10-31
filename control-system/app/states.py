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
    #Safe box temperature
    current_in_temp = 20
    #Safe box humidity
    current_in_hum = 50
    #External temperature
    current_ex_temp = 20
    #Air conditioner temperature change rate
    air_cond_interaction = 0.0
    #Safe box temperature minimum temperature
    min_temp = 20
    #Safe box temperature maximum temperature
    max_temp = 21

    #MQTT client
    mqtt = None

    def __init__(self):
        #Gets args
        ap = argparse.ArgumentParser()
        ap.add_argument("-s", "--simulated", type=int, help="simulated environment")
        args = vars(ap.parse_args())

        #Starts and connect MQTT client to AWS MQTT Broker
        self.mqtt = Mqtt()
        self.mqtt.connect()

        #Simulation case 1:
        #Internal temperature from NODEMCU
        #Internal humidity from potentiometer
        #Air conditioner from NODEMCU
        #External temperature from potentiometer
        if args["simulated"] == 1:
            self.internalSensor = SimulatedEnvironment(None)
            self.internalSensor.start()
            self.airCondControl = self.internalSensor
            self.externalSensor = self.internalSensor
        #Simulation case 2:
        #Internal temperature from NODEMCU
        #Internal humidity from DHT22
        #Air conditioner from NODEMCU
        #External temperature from DHT22
        elif args["simulated"] == 2:
            self.internalSensor = SimulatedEnvironment(Dht22(22))
            self.internalSensor.start()
            self.airCondControl = self.internalSensor
            self.externalSensor = Dht22(23)
            self.externalSensor.start()
        #Simulation case 3:
        #Internal temperature from DHT22(1)
        #Internal humidity from DHT22(1)
        #Air conditioner from NODEMCU
        #External temperature from DHT22(2)
        else:
            self.internalSensor = Dht22(22)
            self.internalSensor.start()
            self.airCondControl = SimulatedEnvironment(None)
            self.airCondControl.start()
            self.externalSensor = Dht22(23)
            self.externalSensor.start()

        #Read initial data from sensors
        self.current_in_temp = self.internalSensor.read("IN_TEMP")
        self.current_in_hum = self.internalSensor.read("IN_HUM")
        self.current_ex_temp = self.externalSensor.read("EX_TEMP")

        #Publish initial data on respective topics
        self.mqtt.publish("pgcc008/problem01/sensor/internal/temperature", self.current_in_temp)
        self.mqtt.publish("pgcc008/problem01/sensor/internal/humidity", self.current_in_hum)
        self.mqtt.publish("pgcc008/problem01/sensor/internal/air_cond_state", self.air_cond_interaction)
        self.mqtt.publish("pgcc008/problem01/sensor/external/temperature", self.current_ex_temp)
        print("[DEVICE] Control System started")

    #Reads all sensors
    def readSensors(self):
        #Gets read time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        #Checks update on temperature range and change this range.
        newRange = False
        #Minimum
        newData = self.mqtt.dataSubscribed[0]
        if newData != self.min_temp:
            self.min_temp = newData
            newRange = True
        #Maximum
        newData = self.mqtt.dataSubscribed[1]
        if newData != self.max_temp:
            self.max_temp = newData
            newRange = True

        if newRange is True:
            print("[DEVICE at", current_time+"] Internal temperature range: "+str(self.min_temp)+" to "+str(self.max_temp)+"C")

        #Checks internal temperature change, updates and publish on topic
        next_in_temp = self.internalSensor.read("IN_TEMP")
        if next_in_temp != self.current_in_temp:
            self.current_in_temp = next_in_temp
            self.mqtt.publish("pgcc008/problem01/sensor/internal/temperature", self.current_in_temp)
            print("[DEVICE at", current_time+"] Internal temperature: "+str(self.current_in_temp)+"C")

        #Checks internal humidity change, updates and publish on topic
        next_in_hum = self.internalSensor.read("IN_HUM")
        if next_in_hum != self.current_in_hum:
            self.current_in_hum = next_in_hum
            self.mqtt.publish("pgcc008/problem01/sensor/internal/humidity", self.current_in_hum)
            print("[DEVICE at", current_time+"] Internal humidity: "+str(self.current_in_hum)+"%")

        #Checks external temperature change, updates and publish on topic
        next_ex_temp = self.externalSensor.read("EX_TEMP")
        if next_ex_temp != self.current_ex_temp:
            self.current_ex_temp = next_ex_temp
            self.mqtt.publish("pgcc008/problem01/sensor/external/temperature", self.current_ex_temp)
            print("[DEVICE at", current_time+"] External temperature: "+str(self.current_ex_temp)+"C")

    #Sends air conditioner command
    def sendAirCondCommand(self, command):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        previous_cond_interaction = self.air_cond_interaction
        air_cond_change_rate = 0.0

        #Checks command to heating safe box
        if command == "heating":
            #Calculates Heating rate (minmum = 0.1C/min)
            air_cond_change_rate = 1 - ((self.current_in_temp - self.current_ex_temp)*0.05)
            if air_cond_change_rate < 0.0:
                air_cond_change_rate = 0.1

        #Calculates Cooling rate (maximum = -0.1C/min)
        elif command == "cooling":
            air_cond_change_rate = 1 - ((self.current_ex_temp - self.current_in_temp)*0.05)
            air_cond_change_rate = -air_cond_change_rate
            if air_cond_change_rate > 0.0:
                air_cond_change_rate = -0.1

        self.air_cond_interaction = float('%.2f' % air_cond_change_rate)

        #Checks change on cooling or heating rate, sends command to change temperature and publish on topic
        if previous_cond_interaction != self.air_cond_interaction:
            self.airCondControl.write(str(self.air_cond_interaction))
            print("[DEVICE at", current_time+"] Air conditioner state: "+command+" ("+str(self.air_cond_interaction)+"C/min)")
            self.mqtt.publish("pgcc008/problem01/sensor/internal/air_cond_state", self.air_cond_interaction)

    #Finishs application
    def stop(self):
        #Turn off air conditioner
        self.sendAirCondCommand("off")
        #Stop all sensors
        self.internalSensor.stopRead()
        self.externalSensor.stopRead()
        self.airCondControl.stopRead()
        #Closes connection with MQTT broker
        self.mqtt.disconnect()
