import matplotlib.pyplot as plt
from cv2 import aruco
import cv2
import numpy as np

# load the ArUCo dictionary
arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

tag = np.zeros((300, 300, 1), dtype="uint8")
aruco.drawMarker(arucoDict, 6, 300, tag, 1)


cv2.imwrite('tag.png', tag)
cv2.imshow("ArUCo Tag", tag)
cv2.waitKey(0)
