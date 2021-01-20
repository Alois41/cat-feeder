import os
import time
import digitalio
from adafruit_motor import stepper
from threading import Thread
import time
import board
import digitalio
from adafruit_motor import stepper

DELAY = 0.01
STEPS = 5000

# To use with a Raspberry Pi:
coils = (
    digitalio.DigitalInOut(board.D19),  # A1
    digitalio.DigitalInOut(board.D26),  # A2
    digitalio.DigitalInOut(board.D20),  # B1
    digitalio.DigitalInOut(board.D21),  # B2
)

for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT

motor = stepper.StepperMotor(coils[0], coils[1], coils[2], coils[3], microsteps=None)


class Distribute(Thread):
    def __init__(self, shared_weight, program_lock):
        super().__init__()
        self.running = True
        self.__steps = 10
        self.target_weight = 150
        self.shared_weight = shared_weight
        self.required = False
        self.program_lock = program_lock

    def add(self, weight):
        self.target_weight = weight
        self.required = True
        self.program_lock.acquire()

    def run(self) -> None:
        while self.running:
            if self.required:
                if self.shared_weight.value <= self.target_weight:
                    motor.onestep()
                    time.sleep(DELAY)
                else:
                    self.required = False
                    if self.program_lock.locked():
                        self.program_lock.release()
