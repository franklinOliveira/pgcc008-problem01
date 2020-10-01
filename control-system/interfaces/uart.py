import serial

class Uart():
    #Init UART
    def __init__(self):
        self.serialPort = serial.Serial("/dev/serial0", 9600, timeout=0.5)

    #Read data.
    def read(self):
        return self.serialPort.readline()

    #Write data.
    def write(self, data):
        self.serialPort.write(data)

    #Close uart
    def close(self):
        self.serialPort.close()
