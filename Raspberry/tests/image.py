from skimage.filters import threshold_yen
from skimage.exposure import rescale_intensity
import cv2
import matplotlib.pyplot as plt


img = cv2.imread('test002.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

yen_threshold = threshold_yen(img)
bright = rescale_intensity(img, (0, yen_threshold), (0, 1))

plt.imshow(bright)
plt.show()

