import adafruit_ads1x15.ads1015 as ADS
import board
import busio
from adafruit_ads1x15.analog_in import AnalogIn
import time
from threading import Thread, Lock
import paho.mqtt.client as mqtt
from multiprocessing import Value
import numpy as np


class Weight_publisher(Thread):
    def __init__(self, client: mqtt.Client, lock: Lock, shared_weight: Value):
        super().__init__()
        self.client = client
        self.lock = lock
        i2c = busio.I2C(board.SCL, board.SDA)

        ads = ADS.ADS1015(i2c)
        ads.gain = 16
        self.chan = AnalogIn(ads, ADS.P0, ADS.P1)
        self.running = True
        self.delay = 0
        self.shared_weight = shared_weight
        self.values = [0] * 500

    def run(self) -> None:
        i = 0
        while self.running:
            i += 1
            self.values.append(5.2405 * self.chan.value + 488.04)
            if len(self.values) > 50:
                self.values.pop(0)

            mean = np.mean(self.values)
            self.shared_weight.value = int(mean)

            if i == 100:
                i=0
                with self.lock:
                    self.client.publish("feeder/weight", int(mean))
