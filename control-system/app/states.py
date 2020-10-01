import argparse
import sys
sys.path.append('/home/pi/control-system/interfaces')
sys.path.append('/home/pi/control-system/sensors')
from uart import Uart

class States:
    current_in_temp = 0
    air_cond_command = b'O'
    min_temp = 20.0
    max_temp = 25.0

    def __init__(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-s", "--simulated", type=int, help="simulated environment")
        args = vars(ap.parse_args())

        if args["simulated"] == 1:
            self.internSensor = Uart()
            self.airCondControl = self.internSensor

    def readSensors(self):
        try:
            self.current_in_temp = float(self.internSensor.read().decode("utf-8"))
        except:
            None

    def controlAirCond(self):
        self.airCondControl.write(self.air_cond_command)

    def off(self):
        self.air_cond_command = b'O'

    def heating(self):
        self.air_cond_command = b'H'

    def cooling(self):
        self.air_cond_command = b'C'
