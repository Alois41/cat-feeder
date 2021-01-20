import cv2
from PIL import Image

catface_cascade = cv2.CascadeClassifier('./cat_cascade.xml')

size = 600, 600

camera = cv2.VideoCapture(0)


# First image retouches
while True:
    _, image = camera.read()
    image = cv2.resize(image, size)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cat_faces = catface_cascade.detectMultiScale(image, scaleFactor=1.3,
                                                 minNeighbors=5, minSize=(10, 10))

    print(cat_faces)
    for (i, (x, y, w, h)) in enumerate(cat_faces):
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.putText(image, "Cat Faces - #{}".format(i + 1), (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

    cv2.imshow("", image)
    cv2.waitKey(1)
