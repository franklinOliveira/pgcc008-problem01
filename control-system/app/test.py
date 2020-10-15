import sys
sys.path.append('/home/franklin/Desktop/Projetos/pgcc008-problem01/control-system/interfaces')
from mqtt import Mqtt

mqtt = Mqtt()
mqtt.connect()

while True:
    index = int(input("[1] - Temperatura interna\n[2] - Umidade interna\n[3] - Estado do ar condicionado\n[4] - Temperatura externa\nEscolha uma opção: "))
    value = input("Informe o valor: ")

    if not index == 3:
        value = float(value)

    topic = ""
    if index == 1:
        topic = "pgcc008/problem01/sensor/internal/temperature"
    elif index == 2:
        topic = "pgcc008/problem01/sensor/internal/humidity"
    elif index == 3:
        topic = "pgcc008/problem01/sensor/internal/air_cond_state"
    elif index == 4:
        topic = "pgcc008/problem01/sensor/external/temperature"

    mqtt.publish(topic, value)

    print("")
mqtt.disconnect()
