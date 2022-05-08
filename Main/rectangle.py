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


def rectangle(mode, rendering):
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.5)

        # initialize bouncebot
        bb = BounceBot()

        # initialize object detector
        detector = ObjectDetector()

        # initialize state
        state = 'straight'

        # parameters
        show_video = True if rendering == 1 else False

        # distances to travel (in cm)
        distances = [distance_to_time(200), distance_to_time(100), distance_to_time(200), distance_to_time(100)]
        time_correction = 0
        turns = 0
        has_dodged = False

        # initialize timer
        timer = Timer()
        timer.start_timer()

        try:
            bb.move(1)
            bb.set_camera_top_servo_angle(-20)
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                print(f'{state = }')

                if mode == 2 and not has_dodged:
                    obj, direction = detector.check_for_object(frame=frame.array, distance_to_dodge=200,
                                                               show_video=show_video)
                    if obj is not None:
                        print("OBJECT DETECTED!")
                        timer.pause_timer()
                        bb.move(0)
                        bb.around_obstacle(direction=direction)
                        has_dodged = True
                        time_correction += distance_to_time(80)
                        timer.resume_timer()
                        bb.move(1)

                if state == 'straight':
                    if timer.get_timer() > distances[turns] - time_correction:
                        if turns < 4:
                            state = 'turn'
                            turns += 1
                            time_correction = 0
                        else:
                            bb.move(0)
                            break  # back at start

                elif state == 'turn':
                    bb.turn_90()
                    state = 'straight'
                    # turns = turns + 1 # if index != 3 else 0
                    timer.start_timer()
                    bb.move(1)

                if mode == 1 and show_video:
                    cv2.imshow("video", frame.array)  # OpenCV image show
                rawCapture.truncate(0)  # Release cache

                # quit on keypress
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            camera.close()
            rawCapture.close()
            pygame.quit()
            bb.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--challenge_num", help="specifies which challenge the code runs on [1/2]", default=1,
                        type=int)
    parser.add_argument("-r", "--rendering", help="render video?", default=1, type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rectangle(args.challenge_num, args.rendering)