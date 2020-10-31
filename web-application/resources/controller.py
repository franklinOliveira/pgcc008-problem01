from mqtt import Mqtt
from datetime import datetime
from datetime import date
import os.path
import csv
import matplotlib.pyplot as plt

class Controller:
    #Safe box temperature minimum temperature
    min_temp = 20
    #Safe box temperature maximum temperature
    max_temp = 21
    #Safe box temperature
    current_in_temp = 0
    #Safe box humidity
    current_in_hum = 0
    #Air conditioner temperature change rate
    current_in_air_cond_state = 0
    #External temperature
    current_ex_temp = 0

    #Daily sensors sample
    daily_samples = list()
    #Automatic routine data
    simulation_data = list()

    #MQTT client
    mqtt = None

    #Path to application folder
    ROOT_PATH = "/home/franklin/Desktop/Projetos/pgcc008-problem01/web-application/"

    def __init__(self):
        #Starts and connect MQTT client to AWS MQTT Broker
        self.mqtt = Mqtt()
        self.mqtt.connect()

        #Stats loading data
        self.loadData()
        self.loadSimulation()

    #Refresh all data readed to a new sample
    def refreshData(self):
        #Gets read time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        #Data update check
        newData = False

        #Checks if automatic routine is enabled
        if len(self.simulation_data) > 0:
            #Checks if is time to change temperature range
            if self.simulation_data[0][0] == current_time:
                self.min_temp = self.simulation_data[0][1]
                self.max_temp = self.simulation_data[0][2]
                self.mqtt.publish("pgcc008/problem01/limit/min", self.min_temp)
                self.mqtt.publish("pgcc008/problem01/limit/max", self.max_temp)
                print("[SERVER at", current_time+"] Internal temperature range: "+str(self.min_temp)+" to "+str(self.max_temp)+"C")
                del(self.simulation_data[0])

        #Checks current internal temperature changes and updates
        if self.current_in_temp != self.mqtt.dataSubscribed[0]:
            self.current_in_temp = self.mqtt.dataSubscribed[0]
            print("[SERVER at", current_time+"] Internal temperature: "+str(self.current_in_temp)+"C")
            newData = True

        #Checks current internal humidity changes and updates
        if self.current_in_hum != self.mqtt.dataSubscribed[1]:
            self.current_in_hum = self.mqtt.dataSubscribed[1]
            print("[SERVER at", current_time+"] Internal humidity: "+str(self.current_in_hum)+"%")
            newData = True

        #Checks current internal air conditioner changes and updates
        if self.current_in_air_cond_state != self.mqtt.dataSubscribed[2]:
            self.current_in_air_cond_state = self.mqtt.dataSubscribed[2]
            if self.current_in_air_cond_state == 0.0:
                print("[SERVER at", current_time+"] Air conditioning state: off")
            elif self.current_in_air_cond_state > 0.0:
                print("[SERVER at", current_time+"] Air conditioning state: heating ("+str(self.current_in_air_cond_state)+"C/min)")
            elif self.current_in_air_cond_state < 0.0:
                print("[SERVER at", current_time+"] Air conditioning state: cooling ("+str(self.current_in_air_cond_state)+"C/min)")
            newData = True

        #Checks current external temperature changes and updates
        if self.current_ex_temp != self.mqtt.dataSubscribed[3]:
            self.current_ex_temp = self.mqtt.dataSubscribed[3]
            print("[SERVER at", current_time+"] External temperature: "+str(self.current_ex_temp)+"C")
            newData = True

        #Save a new daily sample
        sample = [current_time, self.current_in_temp, self.current_in_hum, self.current_in_air_cond_state, self.current_ex_temp]
        self.saveData(sample)

        #Refresh graphs
        if newData == True or int(now.strftime("%S")) == 0:
            self.plotCharts()

    #Saves daily samples on a file
    def saveData(self, sample):
        today = date.today()
        current_date = today.strftime("%Y/%m/%d")

        #Path to daily samples file
        path = self.ROOT_PATH +"files/"+current_date.replace('/', '-')+".csv"

        #Starts a new daily sample file
        fileExists = True
        if not os.path.isfile(path):
            fileExists = False
            self.daily_samples = list()

        #Open daily sample file and write new sample
        with open(path, 'a') as file:
            file_writer = csv.writer(file)
            if fileExists is False:
                file_writer.writerow(["time", "in_temp", "in_hum", "in_air_cond_state", "ex_temp"])
                file_writer.writerow([sample[0], 0.0, 0.0, 0.0, 0.0])
            file_writer.writerow(sample)

        #Saves sample
        self.daily_samples.append(sample)

    #Load current daily samples if exists
    def loadData(self):
        today = date.today()
        day = today.strftime("%Y/%m/%d")

        #Path to daily samples file
        path = self.ROOT_PATH +"files/"+day.replace('/', '-')+".csv"

        #Reads daily samples file and saves data on daily_samples list
        self.daily_samples = list()
        if os.path.isfile(path):
            with open(path, 'r') as file:
                file_reader = csv.reader(file)
                firstRead = True

                for row in file_reader:
                    if firstRead is True:
                        firstRead = False
                    else:
                        sample = [row[0], float(row[1]), float(row[2]), float(row[3]), float(row[4])]
                        self.daily_samples.append(sample)

                nSamples = len(self.daily_samples)
                self.current_in_temp = self.daily_samples[nSamples - 1][1]
                self.current_in_hum = self.daily_samples[nSamples - 1][2]
                self.current_in_air_cond_state = self.daily_samples[nSamples - 1][3]
                self.current_ex_temp = self.daily_samples[nSamples - 1][4]

                self.mqtt.dataSubscribed[0] = self.current_in_temp
                self.mqtt.dataSubscribed[1] = self.current_in_hum
                self.mqtt.dataSubscribed[2] = self.current_in_air_cond_state
                self.mqtt.dataSubscribed[3] = self.current_ex_temp

                #Plots chats
                self.plotCharts()

    #Plots chats
    def plotCharts(self):
        time_axis = list()
        in_temp_axis = list()
        in_hum_axis = list()
        in_air_cond_state_axis = list()
        ex_temp_axis = list()

        #current_time =
        #Creates multiple y-axis
        for sample in self.daily_samples:
            time_axis_sample = int(sample[0][0:2]) + float((int(sample[0][3:5]) * 60) + int(sample[0][6:8]))/3600.0
            time_axis.append(time_axis_sample)
            in_temp_axis.append(sample[1])
            in_hum_axis.append(sample[2])
            in_air_cond_state_axis.append(sample[3])
            ex_temp_axis.append(sample[4])

        #Plots all charts and save figure to show
        plt.plot(time_axis, in_temp_axis)
        plt.grid()
        plt.savefig(self.ROOT_PATH+"static/images/charts/in_temp.png", transparent=True)
        plt.clf()

        plt.plot(time_axis, ex_temp_axis)
        plt.grid()
        plt.savefig(self.ROOT_PATH+"static/images/charts/ex_temp.png", transparent=True)
        plt.clf()

        plt.plot(time_axis, in_hum_axis)
        plt.grid()
        plt.savefig(self.ROOT_PATH+"static/images/charts/in_hum.png", transparent=True)
        plt.clf()

        plt.plot(time_axis, in_air_cond_state_axis)
        plt.grid()
        plt.savefig(self.ROOT_PATH+"static/images/charts/in_air_cond_state.png", transparent=True)
        plt.clf()

    #Loads simulation file and define a automatic interaction routine
    def loadSimulation(self):
        path = self.ROOT_PATH +"files/simulation.csv"

        if os.path.isfile(path):
            with open(path, 'r') as file:
                file_reader = csv.reader(file)
                firstRead = True

                for row in file_reader:
                    if firstRead is True:
                        firstRead = False
                    else:
                        sample = [row[0], int(row[1]), int(row[2])]
                        self.simulation_data.append(sample)

    #Increase or decrease minimum temperature
    def changeMinTemp(self, increase):
        confirmation = False
        if increase is True:
            #Checks relation between minimum and maximum temperatures.
            if (self.min_temp + 1) < self.max_temp:
                self.min_temp = self.min_temp + 1
                self.mqtt.publish("pgcc008/problem01/limit/min", self.min_temp)
                confirmation = True
        else:
            self.min_temp = self.min_temp - 1
            self.mqtt.publish("pgcc008/problem01/limit/min", self.min_temp)
            confirmation = True

        if confirmation is True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("[SERVER at", current_time+"] Internal temperature range: "+str(self.min_temp)+" to "+str(self.max_temp)+"C")

        return confirmation

    #Increase or decrease maximum temperature
    def changeMaxTemp(self, increase):
        confirmation = False

        if increase is True:
            #Checks relation between minimum and maximum temperatures.
            self.max_temp = self.max_temp + 1
            self.mqtt.publish("pgcc008/problem01/limit/max", self.max_temp)
            confirmation = True
        else:
            if (self.max_temp - 1) > self.min_temp:
                self.max_temp = self.max_temp - 1
                self.mqtt.publish("pgcc008/problem01/limit/max", self.max_temp)
                confirmation = True

        if confirmation is True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("[SERVER at", current_time+"] Internal temperature range: "+str(self.min_temp)+" to "+str(self.max_temp)+"C")

        return confirmation

    #Returns temperature on display format
    def getTempFormatted(self, variable):
        if variable == "MIN":
            temp = self.min_temp
        elif variable == "MAX":
            temp = self.max_temp
        elif variable == "IN_TEMP":
            temp = self.current_in_temp
        elif variable == "EX_TEMP":
            temp = self.current_ex_temp

        temp_form = str(int(temp))+'º'

        if temp >= 0 and temp < 10:
            temp_form = '0'+str(int(temp))+'º'

        return temp_form

    #Returns humidity on display format
    def getHumFormatted(self):
        hum_form = str(int(self.current_in_hum))+'%'
        if self.current_in_hum >= 0 and self.current_in_hum < 10:
            hum_form = '0'+str(int(self.current_in_hum))+'%'
        return hum_form

    #Returns air conditioner on display format
    def getAirCondState(self):
        air_cond_state_form = "DES"
        if self.current_in_air_cond_state > 0.0:
            air_cond_state_form = "AQU"
        if self.current_in_air_cond_state < 0.0:
            air_cond_state_form = "RES"
        return air_cond_state_form
