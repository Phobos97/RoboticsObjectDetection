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
from ObjectDetection.aruco.aruco_detector import ArucoDetector
from RobotControl.bouncebot_control import BounceBot
from RobotControl.plot_distance_vs_time import distance_to_time


def bounce(rendering, ball_color):
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.5)

        # initialize bouncebot
        bb = BounceBot()

        # initialize ball detector
        ball_detector = BallDetector(ball_color, offset=20, deadzone=70, fire_trigger_timing=5, minimum_size=300)
        aruco_detector = ArucoDetector()

        # parameters
        max_distance = -1   # steps
        current_x = 0
        speed = 5
        solenoid_timeout = 0
        solenoid_delay = 0.1 # s

        # initialize state
        state = 'stand'

        # main loop
        try:
            # continuous video stream
            for raw_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # get frame, flipped
                frame = cv2.flip(raw_frame.array, -1)

                print(f'{state = }')
                # print(f'{current_x = }')

                angle, frame = aruco_detector.detect_markers(frame)
                direction, fire, frame = ball_detector.check_for_object(frame)

                state = direction

                if angle:
                    bb.set_turret_servo_angle(angle)

                if fire and solenoid_timeout == 0:
                    print('FIRE!')
                    bb.activate_solenoid(0.1, solenoid_delay)
                    bb.activate_solenoid(0.1, solenoid_delay)
                    bb.activate_solenoid(0.1, solenoid_delay)
                    solenoid_timeout = 5

                # check if in bounds
                # if current_x > max_distance:
                #     print('out of bounds right')
                #     if state == 'right':
                #         state = 'stand'
                # elif current_x < -max_distance:
                #     print('out of bounds left')
                #     if state == 'left':
                #         state = 'stand'

                if solenoid_timeout > 0:
                    solenoid_timeout -= 1
                
                if state == 'stand':
                    bb.move(0)

                elif state == 'left':
                    bb.move(-speed)
                    current_x -= 1

                elif state == 'right':
                    bb.move(speed)
                    current_x += 1

                if rendering:
                    cv2.imshow("video", frame)  # OpenCV image show
                # clear the stream in preparation for the next frame
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
    parser.add_argument("-r", "--rendering", help="render video?", action="store_true")
    parser.add_argument("-c", "--ball_color", help="color of the ball [blue/green/yellow/red/pink/purple]",\
                        default="red")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    bounce(args.rendering, args.ball_color)
