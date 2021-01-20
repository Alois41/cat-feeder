import paho.mqtt.client as mqtt
from threads.weight import Weight_publisher
from threads.distribute import Distribute
from threads.recognize import Recognize
import time
from threading import Lock
from multiprocessing import Value
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

app_log = logging

QUANTITY = 0
NUMBER = 1

client_name = "feeder"

shared_weight = Value("i", 0)
program_lock = Lock()
distrib_thread = Distribute(shared_weight, program_lock)
mqtt_lock = Lock()


reglisse = [0, 1]
lilou = [0, 1]

today_reglisse = 0
today_lilou = 0

qLilou = 0
qReglisse = 0

date = datetime.today().date()


def reset_croquettes():
    global today_lilou, today_reglisse, qLilou, qReglisse
    global lilou, reglisse
    today_reglisse = reglisse[QUANTITY]
    today_lilou = lilou[QUANTITY]
    qLilou = max(0, lilou[QUANTITY]) / max(1, lilou[NUMBER])
    qReglisse = max(0, reglisse[QUANTITY]) / max(1, reglisse[NUMBER])
    app_log.info("lilou: %i x%i" % (qLilou, lilou[NUMBER]))
    app_log.info("reglisse: %i x%i" % (qReglisse, reglisse[NUMBER]))


def on_message(client, userdata, message):
    global today_lilou, today_reglisse, lilou, reglisse, date

    if date < datetime.today().date():
        reset_croquettes()
        date = datetime.today().date()

    if message.topic == "feeder/settings/reglisse/quantity":
        reglisse[QUANTITY] = int(str(message.payload.decode("utf-8")))
        reset_croquettes()

    if message.topic == "feeder/settings/reglisse/number":
        reglisse[NUMBER] = int(str(message.payload.decode("utf-8")))
        reset_croquettes()

    if message.topic == "feeder/settings/lilou/quantity":
        lilou[QUANTITY] = int(str(message.payload.decode("utf-8")))
        reset_croquettes()

    if message.topic == "feeder/settings/lilou/number":
        lilou[NUMBER] = int(str(message.payload.decode("utf-8")))
        reset_croquettes()

    if message.topic == "feeder/distribute":
        value = str(message.payload.decode("utf-8"))
        if value == "lilou" and today_lilou > 0:
            today_lilou -= qLilou
            distrib_thread.add(qLilou)
            with mqtt_lock:
                client.publish("feeder/history/lilou/last", str(qLilou) + "," + str(datetime.now()), retain=True)
                client.publish("feeder/history/lilou/restant", str(today_lilou), retain=True)

        elif value == "reglisse" and today_reglisse > 0:
            today_reglisse -= qReglisse
            distrib_thread.add(qReglisse)
            with mqtt_lock:
                client.publish("feeder/history/reglisse/last", str(qReglisse) + "," + str(datetime.now()), retain=True)
                client.publish("feeder/history/reglisse/restant", str(today_reglisse), retain=True)
        else:
            distrib_thread.add(int(value))


broker_address = "feeder"
# broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client(client_name)  # create new instance
client.on_message = on_message
print("connecting to broker")
client.connect(broker_address)  # connect to broker
client.publish("feeder", "test")

weight_thread = Weight_publisher(client, mqtt_lock, shared_weight)
weight_thread.start()
distrib_thread.start()

reco_thread = Recognize(client, mqtt_lock, program_lock, app_log)
reco_thread.start()

print("MQTT client")
client.subscribe("feeder/#")
while True:
    try:
        client.loop()
    except Exception as e:
        app_log.critical(e)
        break

weight_thread.running = False
distrib_thread.running = False
reco_thread.running = False
