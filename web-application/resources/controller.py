from mqtt import Mqtt
from datetime import datetime
from datetime import date
import os.path
import csv
import matplotlib.pyplot as plt

class Controller:
    min_temp = 20
    max_temp = 21

    current_in_temp = 0
    current_in_hum = 0
    current_in_air_cond_state = 0
    current_ex_temp = 0
    daily_samples = list()

    mqtt = None

    ROOT_PATH = "/home/franklin/Desktop/Projetos/pgcc008-problem01/web-application/"

    def __init__(self):
        self.mqtt = Mqtt()
        self.mqtt.connect()

        today = date.today()
        day = today.strftime("%Y/%m/%d")
        self.loadData(day)

    def refreshData(self):
        now = datetime.now()
        current_time = int(now.strftime("%H")) + (float((int(now.strftime("%M")) * 60) + int(now.strftime("%S")))/3600.0)
        newData = False

        if self.current_in_temp != self.mqtt.dataSubscribed[0]:
            self.current_in_temp = self.mqtt.dataSubscribed[0]
            newData = True

        if self.current_in_hum != self.mqtt.dataSubscribed[1]:
            self.current_in_hum = self.mqtt.dataSubscribed[1]
            newData = True

        if self.current_in_air_cond_state != self.mqtt.dataSubscribed[2]:
            self.current_in_air_cond_state = self.mqtt.dataSubscribed[2]
            newData = True

        if self.current_ex_temp != self.mqtt.dataSubscribed[3]:
            self.current_ex_temp = self.mqtt.dataSubscribed[3]
            newData = True

        sample = [current_time, self.current_in_temp, self.current_in_hum, self.current_in_air_cond_state, self.current_ex_temp]
        self.saveData(sample)

        if newData == True or int(now.strftime("%S")) == 0:
            self.plotCharts()



    def saveData(self, sample):
        today = date.today()
        current_date = today.strftime("%Y/%m/%d")
        path = self.ROOT_PATH +"files/"+current_date.replace('/', '-')+".csv"

        fileExists = True
        if not os.path.isfile(path):
            fileExists = False
            self.daily_samples = list()

        with open(path, 'a') as file:
            file_writer = csv.writer(file)
            if fileExists is False:
                file_writer.writerow(["time", "in_temp", "in_hum", "in_air_cond_state", "ex_temp"])
            file_writer.writerow(sample)

        self.daily_samples.append(sample)


    def loadData(self, day):
        path = self.ROOT_PATH +"files/"+day.replace('/', '-')+".csv"

        self.daily_samples = list()
        if os.path.isfile(path):
            with open(path, 'r') as file:
                file_reader = csv.reader(file)
                firstRead = True

                for row in file_reader:
                    if firstRead is True:
                        firstRead = False
                    else:
                        sample = [float(row[0]), float(row[1]), float(row[2]), int(row[3]), float(row[4])]
                        self.daily_samples.append(sample)

                today = date.today()
                current_date = today.strftime("%Y/%m/%d")

                if day == current_date:
                    nSamples = len(self.daily_samples)
                    self.current_in_temp = self.daily_samples[nSamples - 1][1]
                    self.current_in_hum = self.daily_samples[nSamples - 1][2]
                    self.current_in_air_cond_state = self.daily_samples[nSamples - 1][3]
                    self.current_ex_temp = self.daily_samples[nSamples - 1][4]

                    self.mqtt.dataSubscribed[0] = self.current_in_temp
                    self.mqtt.dataSubscribed[1] = self.current_in_hum
                    self.mqtt.dataSubscribed[2] = self.current_in_air_cond_state
                    self.mqtt.dataSubscribed[3] = self.current_ex_temp

                self.plotCharts()

    def plotCharts(self):
        time_axis = list()
        in_temp_axis = list()
        in_hum_axis = list()
        in_air_cond_state_axis = list()
        ex_temp_axis = list()

        for sample in self.daily_samples:
            time_axis.append(sample[0])
            in_temp_axis.append(sample[1])
            in_hum_axis.append(sample[2])
            in_air_cond_state_axis.append(sample[3])
            ex_temp_axis.append(sample[4])

        plt.plot(time_axis, in_temp_axis)
        plt.savefig(self.ROOT_PATH+"static/images/charts/in_temp.png", transparent=True)
        plt.clf()

        plt.plot(time_axis, ex_temp_axis)
        plt.savefig(self.ROOT_PATH+"static/images/charts/ex_temp.png", transparent=True)
        plt.clf()

        plt.plot(time_axis, in_hum_axis)
        plt.savefig(self.ROOT_PATH+"static/images/charts/in_hum.png", transparent=True)
        plt.clf()

        plt.plot(time_axis, in_air_cond_state_axis)
        plt.savefig(self.ROOT_PATH+"static/images/charts/in_air_cond_state.png", transparent=True)
        plt.clf()

    def changeMinTemp(self, increase):
        if increase is True:
            if (self.min_temp + 1) < self.max_temp:
                self.min_temp = self.min_temp + 1
                self.mqtt.publish("pgcc008/problem01/limit/min", self.min_temp)
                return True
        else:
            self.min_temp = self.min_temp - 1
            self.mqtt.publish("pgcc008/problem01/limit/min", self.min_temp)
            return True
        return False

    def changeMaxTemp(self, increase):
        if increase is True:
            self.max_temp = self.max_temp + 1
            self.mqtt.publish("pgcc008/problem01/limit/max", self.max_temp)
            return True
        else:
            if (self.max_temp - 1) > self.min_temp:
                self.max_temp = self.max_temp - 1
                self.mqtt.publish("pgcc008/problem01/limit/max", self.max_temp)
                return True
        return False

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

    def getHumFormatted(self):

        hum_form = str(int(self.current_in_hum))+'%'

        if self.current_in_hum >= 0 and self.current_in_hum < 10:
            hum_form = '0'+str(int(self.current_in_hum))+'%'

        return hum_form

    def getAirCondState(self):
        air_cond_state_form = "DES"
        if self.current_in_air_cond_state == 1:
            air_cond_state_form = "AQU"
        if self.current_in_air_cond_state == -1:
            air_cond_state_form = "RES"
        return air_cond_state_form
