import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT

class Mqtt():
    MQTTClient = None
    dataSubscribed = [20,21]

    def __init__(self):
        ROOT_PATH = "/home/pi/control-system/"
        ROOT_CA_PATH = ROOT_PATH+"certificates/AmazonRootCA1.pem.txt"
        KEY_PATH = ROOT_PATH+"certificates/4d327b67ce-private.pem.key"
        CERT_PATH = ROOT_PATH+"certificates/4d327b67ce-certificate.pem.crt"

        self.MQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient("pgcc008-problem01-device")
        self.MQTTClient.configureEndpoint("a18jmvtsiq4e9v-ats.iot.us-east-1.amazonaws.com", 8883)
        self.MQTTClient.configureCredentials(ROOT_CA_PATH, KEY_PATH, CERT_PATH)

        self.MQTTClient.subscribe("pgcc008/problem01/limit/max", 0, self.limitChangeCallback)
        self.MQTTClient.subscribe("pgcc008/problem01/limit/min", 0, self.limitChangeCallback)

    def limitChangeCallback(self, client, userdata, message):
        if message.topic == "pgcc008/problem01/limit/min":
            self.dataSubscribed[0] = float(message.payload.decode("utf-8"))
        else:
            self.dataSubscribed[1] = float(message.payload.decode("utf-8"))

    def connect(self):
        self.MQTTClient.connect()

    def disconnect(self):
        self.MQTTClient.disconnect()

    def publish(self, topic, data):
        self.MQTTClient.publish(topic, data, 1)
