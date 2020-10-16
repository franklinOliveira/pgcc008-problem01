import serial
import Adafruit_ADS1x15
import numpy as np

class SimulatedEnvironment():
    GAIN = 1

    #Init UART
    def __init__(self):
        self.serialPort = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
        self.adc = Adafruit_ADS1x15.ADS1115()
        self.previousInTemp = 20.0
        self.previousInHum = 0.0
        self.previousExTemp = 0.0

    #Read data.
    def read(self, dataType):
        data = None
        if dataType == "IN_TEMP":
            try:
                data = float(self.serialPort.readline().decode("utf-8"))
                self.previousInTemp = data
            except:
                data = self.previousInTemp

        elif dataType == "EX_TEMP":
            data = float('%.2f' % np.interp(float(self.adc.read_adc(1, gain=1)), [4.0,32767.0], [-40.0, 80.0]))
            if abs(data - self.previousExTemp) <= 2.5:
                data = self.previousExTemp
            else:
                self.previousExTemp = data

        elif dataType == "IN_HUM":
            data = float('%.2f' % np.interp(float(self.adc.read_adc(0, gain=1)), [4.0,32767.0], [0, 100]))

            if abs(data - self.previousInHum) <= 2.5:
                data = self.previousInHum
            else:
                self.previousInHum = data

        return data

    #Write data.
    def write(self, data):
        self.serialPort.write(data.encode("utf-8"))

    #Close uart
    def close(self):
        self.serialPort.close()
