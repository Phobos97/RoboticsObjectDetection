import time
from operator import itemgetter

import cv2
from RobotControl.video_playback import read_video
import os
import numpy as np


class ObjectDetector:
    def __init__(self):
        self.red_lower = np.array([136, 87, 111], np.uint8)
        self.red_upper = np.array([180, 255, 255], np.uint8)
        self.kernel = np.ones((1, 1), "uint8")

    def check_for_object(self, frame, show_video=False):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask = cv2.inRange(hsv, self.red_lower, self.red_upper)
        red_mask = cv2.dilate(red_mask, self.kernel)
        contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        largest = 300
        biggest_contour = None

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > largest:
                biggest_contour = contour
                largest = cv2.contourArea(contour)

        if biggest_contour is None:
            if show_video:
                cv2.imshow("Output", frame)
                cv2.waitKey(1)

            return "stand"

        x, y, w, h = cv2.boundingRect(biggest_contour)
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, "BALL", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))

        if x + 0.5*w > 160:
            direction = "right"
        else:
            direction = "left"

        if show_video:
            cv2.imshow("Output", frame)
            cv2.waitKey(1)

        return direction


if __name__ == '__main__':
    detector = ObjectDetector()
    video = read_video(path="../TestVideos/daniel/20220516-165321.h264")

    for frame in video:
        direction = detector.check_for_object(frame, show_video=True)
        print(direction)
        # if direction != "stand":
        #     time.sleep(0.1)


