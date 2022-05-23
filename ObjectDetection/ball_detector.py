import time

import cv2
from RobotControl.video_playback import read_video
import numpy as np


lower_bounds = {
    "red": [136, 87, 111],
    "pink": [145, 100, 20],
    "purple": [125, 50, 20],
    "green": [40, 50, 20],
    "blue": [90, 50, 50],
    "yellow": [25, 50, 20]
}
upper_bounds = {
    "red": [180, 255, 255],
    "pink": [160, 255, 255],
    "purple": [150, 255, 255],
    "green": [85, 255, 255],
    "blue": [150, 255, 255],
    "yellow": [35, 255, 255]
}


class BallDetector:
    def __init__(self, ball_color, offset=0, fire_trigger_timing=20, minimum_size=300):
        self.color_lower = np.array(lower_bounds[ball_color], np.uint8)
        self.color_upper = np.array(upper_bounds[ball_color], np.uint8)

        # bigger offset means it will go to the left earlier
        self.offset = offset

        # how many pixels from the bottom of the screen the object has to be to trigger a fire event
        # 0 means all the way at the bottom
        self.fire_trigger_timing = fire_trigger_timing

        # minimum area (in number of pixels) for an object to count as a detection
        self.minimum_size = minimum_size

    def check_for_object(self, frame, render=False):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        largest = self.minimum_size
        biggest_contour = None

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > largest:
                biggest_contour = contour
                largest = cv2.contourArea(contour)

        if biggest_contour is None:
            return "stand", False

        x, y, w, h = cv2.boundingRect(biggest_contour)
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, "BALL", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))

        fire = False
        if y + h > frame.shape[0] - self.fire_trigger_timing:
            fire = True

        # reverse?
        if x + 0.5*w > frame.shape[1]*0.5 + self.offset:
            direction = "right"
        else:
            direction = "left"

        if render:
            cv2.imshow("Output", frame)

        return direction, fire, frame


if __name__ == '__main__':
    # bigger offset means it will go to the left earlier
    detector = BallDetector(offset=150, fire_trigger_timing=20, minimum_size=300)
    video = read_video(path="../TestVideos/daniel/20220516-165321.h264")

    for frame in video:
        direction, fire = detector.check_for_object(frame, show_video=True)
        if direction != "stand":
            print(direction)
            time.sleep(0.1)
        if fire:
            print(fire)
            time.sleep(0.5)


