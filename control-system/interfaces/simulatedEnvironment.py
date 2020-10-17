import serial
import Adafruit_ADS1x15
import numpy as np
from threading import Thread

class SimulatedEnvironment(Thread):
    GAIN = 1

    #Init UART
    def __init__(self, dht):
        self.serialPort = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
        self.adc = Adafruit_ADS1x15.ADS1115()
        self.in_temp = 20.0
        self.previousInTemp = 20.0
        self.inHum_exTemp = [0.0, 0.0]
        self.previous_inHum_exTemp = [0.0, 0.0]
        self.dht = dht

        if self.dht is not None:
            self.dht.start()

        self.stop = False
        Thread.__init__(self)

    def run(self):
        while self.stop is False:
            try:
                self.in_temp = float(self.serialPort.readline().decode("utf-8"))
                self.previousInTemp = self.in_temp
            except:
                self.in_temp = self.previousInTemp

            if self.dht is None:
                for i in range(2):
                    min,max = [-40,80]
                    if i == 0:
                        min,max = [0,100]

                    self.inHum_exTemp[i] = float('%.2f' % np.interp(float(self.adc.read_adc(i, gain=1)), [4.0,32767.0], [min, max]))
                    if abs(self.inHum_exTemp[i] - self.previous_inHum_exTemp[i]) <= 2.5:
                        self.inHum_exTemp[i] = self.previous_inHum_exTemp[i]
                    else:
                        self.previous_inHum_exTemp[i] = self.inHum_exTemp[i]
            else:
                self.inHum_exTemp[0] = self.dht.read("HUM")
                self.inHum_exTemp[1] = float('%.2f' % np.interp(float(self.adc.read_adc(1, gain=1)), [4.0,32767.0], [-40, 100]))

    #Read data.
    def read(self, dataType):
        data = None
        if dataType == "IN_TEMP":
            data = self.in_temp

        elif dataType == "EX_TEMP":
            data = self.inHum_exTemp[1]

        elif dataType == "IN_HUM":
            data = self.inHum_exTemp[0]
        return data

    #Write data.
    def write(self, data):
        self.serialPort.write(data.encode("utf-8"))

    def stopRead(self):
        self.stop = True
        self.serialPort.close()
        if self.dht is not None:
            self.dht.stopRead()
