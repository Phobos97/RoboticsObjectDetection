import multiprocessing
import time
import argparse
import cv2
import sys
import os
from pathlib import Path

from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame

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


def straight(mode):
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.5)

        # initialize bouncebot
        bb = BounceBot()
        # initialize object detector
        detector = ObjectDetector()
        # initialize timer
        timer = Timer()

        try:
            for i in range(2):
                timer.start_timer()
                bb.move(1)

                for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                    if timer.get_timer() < distance_to_time(200):
                        bb.move(0)
                        break
                    if mode == 2:
                        obj, direction = detector.check_for_object(frame=frame, distance_to_dodge=25, show_video=True)
                        if obj is not None:
                            print("OBJECT DETECTED!")
                            timer.pause_timer()
                            bb.move(0)
                            bb.around_obstacle(direction=direction)
                            timer.resume_timer()
                if i == 0:
                    print("U-TURN")
                    bb.u_turn()
        finally:
            camera.close()
            rawCapture.close()
            pygame.quit()
            bb.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenge_num", help="specifies which challenge the code runs on [1/2/3/4]", default=1)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # m = Manager(mode=args.challenge_num)
    # m.start()

    straight(args.challenge_num)
