import torch
import cv2
from PIL import Image
from modules.Extractor import preprocess, classes
from modules.Classifieur import model
import os

target_classes = ["Egyptian cat", "tabby, tabby cat", "Persian", "Siamese cat, Siamese", "tiger cat"]

if __name__ == '__main__':
    for subdir, dirs, files in os.walk("../videos"):
        for file in files:
            cap = cv2.VideoCapture(os.path.join(subdir, file))
            print(file)
            prefix = file.split(".")[0]
            n = 0
            with torch.no_grad():
                while cap.isOpened():
                    ret, frame = cap.read()
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

                    if ret:
                        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        im_pil = Image.fromarray(img)
                        tensor = preprocess(im_pil).unsqueeze(0)
                        pred = model(tensor)
                        probs = torch.nn.functional.softmax(pred[0], dim=0)
                        values, indices = torch.topk(probs, 3)
                        for c, v in zip([classes[int(i)] for i in indices.squeeze()], values):
                            if c in target_classes and v > .3:
                                filename = "./data/%s/%s_%i.jpg" % (subdir.split("\\")[-1], prefix, n)
                                cv2.imwrite(filename, frame)
                                n += 1
                    else:
                        break

                cap.release()
