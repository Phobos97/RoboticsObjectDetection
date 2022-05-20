import time
import argparse
import cv2
import sys
import os
from pathlib import Path

from picamera.array import PiRGBArray
from picamera import PiCamera

# modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = str(Path(script_dir).parents[0])
sys.path.append(project_root_dir)

from timer import Timer
from ObjectDetection.ball_detector import BallDetector
from RobotControl.bouncebot_control import BounceBot
from RobotControl.plot_distance_vs_time import distance_to_time


def bounce(rendering):
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.5)

        # initialize bouncebot
        bb = BounceBot()

        # initialize ball detector
        detector = BallDetector()

        # initialize timer
        timer = Timer()
        timer.start_timer()
        timer.pause_timer()

        # parameters
        max_distance = 100   # cm, max distance to travel forward/backward
        time_to_max_distance = distance_to_time(max_distance)    # s
        show_video = True if rendering == 1 else False

        # initialize state
        state = 'stand'

        # main loop
        try:
            # initial state
            bb.set_camera_bottom_servo_angle(-90)

            # continuous video stream
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                print(f'{state = }')

                # check if in bounds
                if abs(timer.get_timer()) > time_to_max_distance:
                    print('out of bounds')
                    state = 'stand'
                else:
                    direction, fire = detector.check_for_object(frame, show_video=show_video)
                    state = direction

                    if fire:
                        bb.activate_solenoid(0.2)

            if state == 'stand':
                bb.move(0)
            elif state == 'left':
                timer.reversed = True
                bb.move(-1)
                bb.set_turret_servo_angle(-20)
            elif state == 'right':
                timer.reversed = False
                bb.move(1)
                bb.set_turret_servo_angle(20)

        finally:
            camera.close()
            rawCapture.close()
            bb.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rendering", help="render video?", default=0, type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    bounce(args.rendering)