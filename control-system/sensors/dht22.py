import Adafruit_DHT
from threading import Thread

class Dht22(Thread):
    #Sets the DHT sensor model
    DHT_SENSOR = Adafruit_DHT.DHT22

    #Initializes DHT22.
    def __init__(self, pin):
        #Sets the DHT22 access pin
        self.DHT_PIN = pin
        #Sets start humidity
        self.dataReaded = (50,20)
        #Enable sensor read
        self.stop = False
        Thread.__init__(self)

    #Starts DHT read thread
    def run(self):
        #If sensor read is enabled
        while self.stop is False:
            #Read data
            self.dataReaded = Adafruit_DHT.read_retry(self.DHT_SENSOR, self.DHT_PIN)
            #Check data
            if self.dataReaded[0] is None or self.dataReaded[1] is None:
                self.dataReaded = (50,20)

    #Returns requested data by type
    def read(self, dataType):
        data = 0
        #humidity requested
        if "HUM" in dataType:
            data = self.dataReaded[0]
        #temperature requested
        else:
            data = self.dataReaded[1]
        return float('%.2f' % data)

    #Disable read
    def stopRead(self):
        self.stop = True
