import multiprocessing
import time
import argparse
import cv2
import sys
import os
from pathlib import Path

# modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = str(Path(script_dir).parents[0])
sys.path.append(project_root_dir)

from timer import Timer
from ObjectDetection.object_detection import ObjectDetector
from RobotControl.bouncebot_control import BounceBot
from RobotControl.plot_distance_vs_time import distance_to_time


class Manager:
    def __init__(self, mode):
        self.timer = Timer()
        self.detector = ObjectDetector()
        self.robot = BounceBot()

        self.mode = mode

    # def detect(self):
    #     vcap = cv2.VideoCapture(0)
    #
    #     if vcap.isOpened():
    #         feed = True
    #     else:
    #         feed = False
    #
    #     detector = ObjectDetector()
    #     while feed:
    #         feed, frame = vcap.read()
    #         _, direction = detector.check_for_object(frame=frame, distance_to_dodge=25) # 25?
    #         if direction is not None:
    #             self.timer.pause_timer()

    def avoid(self, direction):
        self.robot.around_obstacle(direction=direction)

    def start(self):
        self.timer.start_timer()
        self.robot.move(1)

        vcap = cv2.VideoCapture(0)
        if vcap.isOpened():
            feed = True
        else:
            feed = False
            raise ValueError("Could not connect to the camera.")

        while self.timer.get_timer() < distance_to_time(200) and feed:
            # object detection
            if self.mode == 2:
                feed, frame = vcap.read()
                obj, avoid_direction = self.detector.check_for_object(frame=frame, distance_to_dodge=25,
                                                                      show_video=True)
                if obj is not None:
                    self.robot.move(0)
                    self.timer.pause_timer()

                    self.avoid(avoid_direction)

                    self.robot.move(1)
                    self.timer.resume_timer()
        self.robot.move(0)

        # supposedly we are at point B
        self.robot.u_turn()

        # pyslam check ?

        # return
        self.timer.start_timer()
        self.robot.move(1)

        while self.timer.get_timer() < distance_to_time(200) and feed:
            # object detection
            if self.mode == 2:
                feed, frame = vcap.read()
                obj, avoid_direction = self.detector.check_for_object(frame=frame, distance_to_dodge=25,
                                                                      show_video=True)
                if obj is not None:
                    self.robot.move(0)
                    self.timer.pause_timer()

                    self.avoid(avoid_direction)

                    self.robot.move(1)
                    self.timer.resume_timer()

        self.robot.move(0)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenge_num", help="specifies which challenge the code runs on \
                            [1-no object avoidance/2-object avoidance]", default=1)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    m = Manager(mode=args.challenge_num)
    m.start()
