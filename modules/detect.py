import cv2
import numpy as np

class Detect:
    def __init__(self):
        super().__init__()
        # Valeur de flou, impair
        self.blur = 41
        # Seuils sur le gris
        self.gray_thr = 60, 255
        # Aire minimal avec différence de pixels
        self.area_thr = 500000
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        # self.first_frame = None

    def process(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (self.blur, self.blur), 0)

        return gray

    def detect(self, frame):
        h_frame, w_frame, _ = frame.shape
        # gray = self.process(frame)

        fgmask = self.fgbg.apply(frame)
        thresh = cv2.threshold(fgmask, 60, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        # x, y, w, h = cv2.boundingRect(thresh)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            if cv2.contourArea(c) > 50000:
                (x, y, w, h) = cv2.boundingRect(c)
                boxed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                boxed_frame = cv2.rectangle(boxed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imwrite("last_box.jpg", boxed_frame)
                return True

        return False


    # def detect(self, frame):
    #     h_frame, w_frame, _ = frame.shape
    #     gray = self.process(frame)
    #     # if self.first_frame is None:
    #     #     self.first_frame = gray
    #     #     return False
    #     # Ecart entre les frames
    #     delta = cv2.absdiff(self.first_frame, gray)
    #
    #     if np.sum(delta) > self.area_thr:
    #         self.first_frame = gray
    #         return True
    #     # Seuil
    #     # thresh = cv2.threshold(delta, *self.gray_thr, cv2.THRESH_BINARY)[1]
    #     # # Dilatation des zones
    #     # thresh = cv2.dilate(thresh, None, iterations=2)
    #     #
    #     # x, y, w, h = cv2.boundingRect(thresh)
    #     # contours, _ = cv2.findContours(thresh, cv2.RETR_TREE,
    #     #                                cv2.CHAIN_APPROX_SIMPLE)
    #     # print(contours)
    #     # for c in contours:
    #     #     print(cv2.contourArea(c))
    #     #     if cv2.contourArea(c) > self.area_thr:
    #     #         self.first_frame = gray
    #     #         return True
    #
    #     return False
