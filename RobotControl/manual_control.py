from bouncebot_control import BounceBot
import pygame
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

import os, sys
from pathlib import Path

# modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = str(Path(script_dir).parents[0])
sys.path.append(project_root_dir)

from ObjectDetection.object_detection import ObjectDetector


class ManualControl:
    def __init__(self, bouncebot, camera):
        self.bouncebot = bouncebot
        self.camera = camera

        # initalize pygame
        pygame.init()

        # set up the window to capture key inputs
        # TODO: not working with ssh?
        # self.display = pygame.display.set_mode((640, 480))
        self.display = pygame.display.set_mode((640, 480), pygame.OPENGL)
        pygame.display.set_caption('BounceBot Manual Control')

        # parameters
        self.speed = 5
        self.recording = False
        self.recording_timeout = 0

        self.solenoid_timeout = 0

    def process_directions(self, directions):
        for i, direction in enumerate(directions):
            if i == 0:
                self.bouncebot.move(direction * self.speed)
            elif i == 1:
                self.bouncebot.turn(direction)
            elif i == 2:
                self.bouncebot.look_vertical(direction)
            elif i == 3:
                self.bouncebot.look_horizontal(direction)
            elif i == 4:
                self.bouncebot.rotate_turret(direction)


    def update(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        directions = np.zeros(5)

        if keys[pygame.K_w]:
            directions[0] += 1    # forward
        if keys[pygame.K_s]:
            directions[0] -= 1    # backward
        if keys[pygame.K_d]:
            directions[1] += 1    # right
        if keys[pygame.K_a]:
            directions[1] -= 1    # left
        if keys[pygame.K_UP]:
            directions[2] += 1    # look up
        if keys[pygame.K_DOWN]:
            directions[2] -= 1    # look down
        if keys[pygame.K_RIGHT]:
            directions[3] += 1    # look right
        if keys[pygame.K_LEFT]:
            directions[3] -= 1    # look left
        if keys[pygame.K_PERIOD]:
            directions[4] += 1    # rotate turret right
        if keys[pygame.K_COMMA]:
            directions[4] -= 1    # rotate turret left
        if keys[pygame.K_HOME]:
            self.bouncebot.reset_servo_angles()

        if keys[pygame.K_SPACE]:   # fire solenoid
            if self.solenoid_timeout == 0:
                self.solenoid_timeout = 10
                self.bouncebot.activate_solenoid(0.2)

        if keys[pygame.K_r]:   # start/stop recording
            if not self.recording and self.recording_timeout == 0:
                self.recording = True
                self.recording_timeout = 24

                print("Recording started")
                self.camera.start_recording(
                    f'videos/{time.strftime("%Y%m%d-%H%M%S")}.h264'
                )
            if self.recording and self.recording_timeout == 0:
                self.recording = False
                self.recording_timeout = 24

                print("Recording stopped")
                self.camera.stop_recording()

        # keep track of these cooldown timers to make sure we don't activate twice
        if self.recording_timeout > 0:
            self.recording_timeout -= 1
        if self.solenoid_timeout > 0:
            self.solenoid_timeout -= 1

        self.process_directions(directions)


def main():
    # initialize camera
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.5)

        # initialize bouncebot
        bb = BounceBot()

        # initialize manual controller
        mc = ManualControl(bb, camera)

        # main control loop
        try:
            for raw_frame in camera.capture_continuous(rawCapture, format="bgr",
                                                   use_video_port=True):  # use_video_port=True
                # get frame, flipped
                frame = cv2.flip(raw_frame.array, -1)

                # update the pygame display
                cv2.imshow("video", frame)  # OpenCV image show
                rawCapture.truncate(0)  # Release cache

                # control the robot
                mc.update()

                # quit on keypress
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print(f'write image')
                    cv2.imwrite(f'images/{time.strftime("%Y%m%d-%H%M%S")}.jpg', frame)

        finally:
            camera.close()
            rawCapture.close()
            pygame.quit()
            bb.close()


if __name__ == "__main__":
    main()
