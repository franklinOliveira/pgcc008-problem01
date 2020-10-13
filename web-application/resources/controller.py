from mqtt import Mqtt

class Controller:
    min_temp = 20
    max_temp = 21
    mqtt = None

    def __init__(self):
        self.mqtt = Mqtt()
        self.mqtt.connect()

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

        temp_form = str(temp)+'º'

        if temp >= 0 and temp < 10:
            temp_form = '0'+str(temp)+'º'

        return temp_form
