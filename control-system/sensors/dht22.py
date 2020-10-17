import Adafruit_DHT
from threading import Thread

class Dht22(Thread):
    #Sets the DHT sensor model
    DHT_SENSOR = Adafruit_DHT.DHT22

    #Initializes DHT22 with i(sensor number) equal 1,2.
    def __init__(self, pin):
        #Sets the DHT22 access pin
        self.DHT_PIN = pin
        self.dataReaded = (0,20)
        self.stop = False
        Thread.__init__(self)

    def run(self):
        while self.stop is False:
            self.dataReaded = Adafruit_DHT.read_retry(self.DHT_SENSOR, self.DHT_PIN)

            if self.dataReaded[0] is None or self.dataReaded[1] is None:
                self.dataReaded = (0,20)

    def read(self, dataType):
        data = 0
        if "HUM" in dataType:
            data = self.dataReaded[0]
        else:
            data = self.dataReaded[1]
        return float('%.2f' % data)

    def stopRead(self):
        self.stop = True
