from RobotControl.bouncebot_control import BounceBot
from ObjectDetection.object_detection import ObjectDetector

import time
import argparse
import multiprocessing

thresh = 0.45

class Timer:
    def __init__(self):
        self.start_time = None
        self.DISTANCE_WAIT = 20
        self.elapsed_time = 0
        self.process = None

    def start(self):
        self.start_time = time.time()

        while self.start_time + self.DISTANCE_WAIT < time

class Move:
    pass


class Obj_Detec:
    def __init__(self):
        self.robot = None
        self.timer = None
        self.detector = ObjectDetector()

    def detect_object(self):



def extract_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--challenge_num', help="define which challenge the robot must run [1-2]", default=1)
    return parser.parse_args()


def start(mode: str):


if __name__ == '__main__':
    args = extract_args()
    start(args.challenge_num)


