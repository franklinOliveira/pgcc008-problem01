# coding: utf-8

import argparse
import sys

sys.path.append('/home/pi/control-system/interfaces')
sys.path.append('/home/pi/control-system/sensors')
from uart import Uart
from mqtt import Mqtt

class States:
    current_in_temp = 20
    air_cond_command = b'O'
    min_temp = 20.0
    max_temp = 21.0

    mqtt = None

    def __init__(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-s", "--simulated", type=int, help="simulated environment")
        args = vars(ap.parse_args())

        self.mqtt = Mqtt()
        self.mqtt.connect()

        if args["simulated"] == 1:
            self.internalSensor = Uart()
            self.airCondControl = self.internalSensor

        print("[INFO] Control System started")
        print("  Internal temperature range: "+str(self.min_temp)+" to "+str(self.max_temp)+"C")
        print("  Internal temperature: "+str(self.current_in_temp)+"C")
        print("  Air conditioning state: off")

    def readSensors(self):
        dataReaded = self.mqtt.dataSubscribed[0]
        if dataReaded != self.min_temp:
            self.min_temp = dataReaded
            print("[INFO] Min internal temperature: "+str(self.min_temp)+"C\t\tSubscribed from 'pgcc008/problem01/limit/min'")

        dataReaded = self.mqtt.dataSubscribed[1]
        if dataReaded != self.max_temp:
            self.max_temp = dataReaded
            print("[INFO] Max internal temperature: "+str(self.max_temp)+"C\t\tSubscribed from 'pgcc008/problem01/limit/max'")

        try:
            dataReaded = float(self.internalSensor.read().decode("utf-8"))
            if dataReaded != self.current_in_temp:
                self.current_in_temp = dataReaded
                self.mqtt.publish("pgcc008/problem01/sensor/internal/temperature", self.current_in_temp)
                print("[INFO] Internal temperature: "+str(self.current_in_temp)+"C\t\tPublished in 'pgcc008/problem01/sensor/internal/temperature'")
        except:
            None

    def sendAirCondCommand(self, command):
        self.air_cond_command = command

        if self.air_cond_command == b'O':
            print("[INFO] Air conditioning state: off")
        elif self.air_cond_command == b'H':
            print("[INFO] Air conditioning state: heating")
        elif self.air_cond_command == b'C':
            print("[INFO] Air conditioning state: cooling")

        self.airCondControl.write(self.air_cond_command)

    def stop(self):
        self.mqtt.disconnect()
        self.sendAirCondCommand(b'O')
