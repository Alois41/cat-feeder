import adafruit_ads1x15.ads1015 as ADS
import board
import busio
from adafruit_ads1x15.analog_in import AnalogIn
import time
import numpy as np

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
ads.gain = 16
chan = AnalogIn(ads, ADS.P0, ADS.P1)
values = []
voltages = []

i = 0
while True:
    i += 1
    values.append(5.2405 * chan.value + 488.04)
    voltages.append(chan.voltage)
    if len(values) > 500:
        values.pop(0)
    if len(voltages) > 500:
        voltages.pop(0)

    if i == 100:
        i = 0
        print("value:, ", np.mean(values))
        print("voltages: ", np.mean(voltages))
