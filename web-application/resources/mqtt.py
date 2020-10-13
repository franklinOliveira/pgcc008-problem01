import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT

class Mqtt():
    MQTTClient = None
    dataSubscribed = [0,0,b'O',0]

    def __init__(self):
        ROOT_PATH = "/home/franklin/Desktop/Projetos/pgcc008-problem01/web-application/resources/"
        ROOT_CA_PATH = ROOT_PATH+"certificates/AmazonRootCA1.pem.txt"
        KEY_PATH = ROOT_PATH+"certificates/a44bf8f189-private.pem.key"
        CERT_PATH = ROOT_PATH+"certificates/a44bf8f189-certificate.pem.crt"

        self.MQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient("pgcc008-problem01-server")
        self.MQTTClient.configureEndpoint("a18jmvtsiq4e9v-ats.iot.us-east-1.amazonaws.com", 8883)
        self.MQTTClient.configureCredentials(ROOT_CA_PATH, KEY_PATH, CERT_PATH)

        self.MQTTClient.subscribe("pgcc008/problem01/sensor/internal/temperature", 0, self.dataChangeCallback)
        self.MQTTClient.subscribe("pgcc008/problem01/sensor/internal/humidity", 0, self.dataChangeCallback)
        self.MQTTClient.subscribe("pgcc008/problem01/sensor/internal/air_cond_state", 0, self.dataChangeCallback)
        self.MQTTClient.subscribe("pgcc008/problem01/sensor/external/temperature", 0, self.dataChangeCallback)

    def dataChangeCallback(self, client, userdata, message):
        if message.topic == "pgcc008/problem01/sensor/internal/temperature":
            self.dataSubscribed[0] = float(message.payload.decode("utf-8"))
        elif message.topic == "pgcc008/problem01/sensor/internal/humidity":
            self.dataSubscribed[1] = float(message.payload.decode("utf-8"))
        elif message.topic == "pgcc008/problem01/sensor/internal/air_cond_state":
            self.dataSubscribed[2] = message.payload.decode("utf-8")
        elif message.topic == "pgcc008/problem01/sensor/external/temperature":
            self.dataSubscribed[3] = float(message.payload.decode("utf-8"))

    def connect(self):
        self.MQTTClient.connect()

    def disconnect(self):
        self.MQTTClient.disconnect()

    def publish(self, topic, data):
        self.MQTTClient.publish(topic, data, 1)
