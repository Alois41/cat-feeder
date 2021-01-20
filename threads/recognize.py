from modules.Extractor import extractor, preprocess, classifier_coarse, custom_classifier, classes
import torch
import cv2
from PIL import Image
from modules.detect import Detect
import time
import paho.mqtt.client as mqtt
from modules import json_load
from threading import Thread, Lock
from datetime import datetime
import os
import json
import logging

targets = ["lilou", 'autre', 'reglisse']


class Recognize(Thread):
    def __init__(self, client: mqtt.Client, mqtt_lock: Lock, program_lock: Lock, log: logging.Logger):
        super().__init__()

        self.log = log
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        extractor.to(self.device)
        classifier_coarse.to(self.device)
        custom_classifier.to(self.device)

        self.results_classes = []
        self.results_target = []

        dummy = torch.ones((1, 3, 224, 224)).to(self.device)
        dummy_2 = extractor(dummy)
        classifier_coarse(dummy_2)
        custom_classifier(dummy)
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.running = True

        self.client = client
        self.mqtt_lock = mqtt_lock
        self.program_lock = program_lock
        self.detecteur = Detect()

        self.animal_classes = []
        with open('./hierachy.json') as json_file:
            data = json.load(json_file)
            sub_dict = json_load.find_cat("mammal, mammalian", data)
            if sub_dict:
                json_load.add_all_cat(self.animal_classes, sub_dict)

        self.animal_classes.remove("West Highland white terrier")
        self.log.info(self.animal_classes)
        self.log.info("Egyptian cat" in self.animal_classes)

    def run(self) -> None:
        while self.running:
            with self.program_lock:
                ret, frame = self.cam.read()
                for i in range(5):
                    ret, frame = self.cam.read()
                frame = cv2.flip(frame, 0)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if not ret:
                    raise IOError("camera issues")

                if not self.detecteur.detect(frame):
                    time.sleep(.2)
                    continue

                self.log.info("movement")

                with torch.no_grad():
                    tensor = preprocess(Image.fromarray(frame)).to(self.device)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    cv2.imwrite("last.jpg", frame)
                    tensor_out = extractor(tensor.unsqueeze(0))
                    target_out = classifier_coarse(tensor_out)
                    target = torch.nn.Softmax(dim=0)(custom_classifier(tensor.unsqueeze(0)).squeeze())
                    target = targets[int(torch.argmax(target))]

                    out = torch.topk(target_out, 5, 1)
                    out_classes = [classes[int(y)].split(",")[0] for y in out[1].squeeze()]

                    self.log.info(target)
                    self.log.info(out_classes)

                    is_animal = False
                    for out_class in out_classes:
                        if out_class in self.animal_classes:
                            self.log.info("animal: %s" % out_class)
                            is_animal = True

                    if is_animal:
                        if target == "lilou":
                            with self.mqtt_lock:
                                self.client.publish("feeder/distribute", "Lilou")


                        elif target == "reglisse":
                            with self.mqtt_lock:
                                self.client.publish("feeder/distribute", "Reglisse")

                        cv2.imwrite("/home/pi/ftp/files/%s-%s-%s.jpg" % (target, ",".join(out_classes), datetime.now()),
                                    frame)

                list_of_files = os.listdir("/home/pi/ftp/files")
                full_path = ["/home/pi/ftp/files/{0}".format(x) for x in list_of_files]

                while len(list_of_files) >= 25:
                    oldest_file = min(full_path, key=os.path.getctime)
                    os.remove(oldest_file)
                    self.log.warning("old picture removed")
                    list_of_files = os.listdir("/home/pi/ftp/files")
                    full_path = ["/home/pi/ftp/files/{0}".format(x) for x in list_of_files]
