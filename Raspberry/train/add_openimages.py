import os
import pandas as pd
from os.path import isfile, join
import shutil
import tqdm

class_to_id = pd.read_csv("D:\Data\OpenImage\id_to_class.csv")
images_ids = pd.read_csv("D:\Data\OpenImage\images_ids.csv")

data = pd.merge(class_to_id, images_ids, on="LabelName")
del class_to_id, images_ids

target_classes = ["Egyptian cat", "tabby, tabby cat", "Persian",
                  "Siamese cat, Siamese", "tiger cat", "Domestic long-haired cat",
                  "Norwegian forest cat", "Cat"]

checkpoint = 3337
path = "d:/Data/OpenImage/train_00"
for n, entry in tqdm.tqdm(enumerate(os.scandir(path))):
    if n < checkpoint:
        continue

    saved = False
    if entry.is_file():
        labels = data.loc[data['ImageID'] == entry.name.split(".")[0]]['DisplayName']
        for label in labels:
            if label in target_classes:
                shutil.copy(entry.path, "./data/Cats/%s_%s" % (label, entry.name))
                saved = True
                break
        if not saved:
            shutil.copy(entry.path, "./data/Others/%s%s" % (list(labels)[0], entry.name))
