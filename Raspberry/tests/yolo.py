import cv2
import time
import numpy as np

img = cv2.imread("test002.jpg")
classes = open('coco.names').read().strip().split('\n')
np.random.seed(42)
colors = np.random.randint(0, 255, size=(len(classes), 3), dtype='uint8')

net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3-spp.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# construct a blob from the image
blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
r = blob[0, 0, :, :]

cv2.imshow('blob', r)
text = f'Blob shape={blob.shape}'
cv2.displayOverlay('blob', text)
cv2.waitKey(1)

net.setInput(blob)
t0 = time.time()
outputs = net.forward(ln)
t = time.time()
print('time=', t - t0)

print(len(outputs))
for out in outputs:
    print(out.shape)


def trackbar2(x):
    confidence = x / 100
    r = r0.copy()
    for output in np.vstack(outputs):
        if output[4] > confidence:
            x, y, w, h = output[:4]
            p0 = int((x - w / 2) * 416), int((y - h / 2) * 416)
            p1 = int((x + w / 2) * 416), int((y + h / 2) * 416)
            cv2.rectangle(r, p0, p1, 1, 1)
    cv2.imshow('blob', r)
    text = f'Bbox confidence={confidence}'
    cv2.displayOverlay('blob', text)


r0 = blob[0, 0, :, :]
r = r0.copy()
cv2.imshow('blob', r)
cv2.createTrackbar('confidence', 'blob', 50, 101, trackbar2)
trackbar2(50)

boxes = []
confidences = []
classIDs = []
h, w = img.shape[:2]

for output in outputs:
    for detection in output:
        scores = detection[5:]
        classID = np.argmax(scores)
        confidence = scores[classID]
        if confidence > 0.5:
            box = detection[:4] * np.array([w, h, w, h])
            (centerX, centerY, width, height) = box.astype("int")
            x = int(centerX - (width / 2))
            y = int(centerY - (height / 2))
            box = [x, y, int(width), int(height)]
            boxes.append(box)
            confidences.append(float(confidence))
            classIDs.append(classID)

indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.3)
if len(indices) > 0:
    for i in indices.flatten():
        (x, y) = (boxes[i][0], boxes[i][1])
        (w, h) = (boxes[i][2], boxes[i][3])
        color = [int(c) for c in colors[classIDs[i]]]
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        text = "{}: {:.4f}".format(classes[classIDs[i]], confidences[i])
        print(text)
        cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

cv2.imshow('window', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
