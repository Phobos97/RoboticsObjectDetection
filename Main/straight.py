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
from ObjectDetection.object_detection import ObjectDetector
from RobotControl.bouncebot_control import BounceBot
from RobotControl.plot_distance_vs_time import distance_to_time


def straight(mode, rendering):
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.5)

        # initialize bouncebot
        bb = BounceBot()

        # initialize object detector
        detector = ObjectDetector(threshold=0.35)

        # initialize state
        state = 'straight'
        has_turned = False

        # parameters
        time_to_drive_2_meters = distance_to_time(200)
        time_correction = 0
        has_dodged = False
        show_video = True if rendering == 1 else False
        dir_bias = 0.5
        dir_angle = 5

        # start stop timer
        ss_timer = Timer()
        ss_time = 0.25 #s
        move = True
        ss_timer.start_timer()

        # initialize timer
        timer = Timer()
        timer.start_timer()

        try:
            # set initial state
            bb.move(1)
            bb.set_camera_top_servo_angle(-21)
            bb.set_camera_bottom_servo_angle(6)
            bb.set_direction_servo_angle(-5)
            bb.set_direction_servo_angle(0)
            time.sleep(0.5)

            # continuous video stream
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                print(f'{state = }')
                print(f'{dir_angle = }')

                # start or stop, and change the direction of the dir_servo
                if ss_timer.get_timer() > ss_time:
                    if move:
                        bb.move(0)
                        move = False
                        timer.pause_timer()
                    else:
                        bb.move(1)
                        move = True
                        dir_angle *= -1
                        bb.set_direction_servo_angle(dir_angle + dir_bias)
                        timer.resume_timer()
                    ss_timer.start_timer()

                # check for obstacles
                if mode == 2 and not has_dodged:
                    obj, direction = detector.check_for_object(frame=frame.array, distance_to_dodge=150,
                                                               all_objects=False, show_video=show_video)
                    if obj is not None:
                        print("OBJECT DETECTED!")

                        # set the robot to moving if it wasn't already
                        if not move:
                            move = True
                            timer.resume_timer()

                        timer.pause_timer()
                        bb.move(0)
                        bb.around_obstacle(direction=direction)
                        time_correction += distance_to_time(80)    # correct for manoeuvre
                        has_dodged = True

                        # prepare to continue straight
                        dir_angle = abs(dir_angle)
                        bb.set_direction_servo_angle(dir_angle + dir_bias)
                        ss_timer.start_timer()
                        timer.resume_timer()
                        bb.move(1)

                # move along a straight line
                if state == 'straight':
                    # turn when the timer is up
                    if timer.get_timer() > time_to_drive_2_meters - time_correction:
                        if not has_turned:
                            state = 'turn'
                            has_turned = True
                        else:
                            bb.move(0)
                            break    # back at marker

                # make a u-turn
                elif state == 'turn':
                    # set the robot to moving if it wasn't already
                    if not move:
                        move = True
                        timer.resume_timer()

                    bb.u_turn()
                    state = 'straight'
                    has_dodged = False
                    timer.start_timer()

                    # prepare to move straight
                    time_correction = 0
                    dir_angle = abs(dir_angle)
                    bb.set_direction_servo_angle(dir_angle + dir_bias)
                    ss_timer.start_timer()
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
            bb.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--challenge_num", help="specifies which challenge the code runs on [1/2]", default=1,
                        type=int)
    parser.add_argument("-r", "--rendering", help="render video?", default=1, type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    straight(args.challenge_num, args.rendering)
