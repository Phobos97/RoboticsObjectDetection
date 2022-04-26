from bouncebot_control import BounceBot
import pygame
import cv2
import os
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time


class ManualControl:
    def __init__(self, bouncebot):
        self.bouncebot = bouncebot

        # initalize pygame
        pygame.init()

        # set up the window to capture key inputs
        # TODO: not working with ssh?
        # self.display = pygame.display.set_mode((640, 480))
        self.display = pygame.display.set_mode((640, 480), pygame.OPENGL)
        pygame.display.set_caption('BounceBot Manual Control')

    def process_directions(self, directions):
        for i, direction in enumerate(directions):
            if i == 0:
                self.bouncebot.move(direction * 30)
            elif i == 1:
                self.bouncebot.turn(direction)
            elif i == 2:
                self.bouncebot.look_vertical(direction)
            elif i == 3:
                self.bouncebot.look_horizontal(direction)
            # elif i == 4:
            #     self.bouncebot.rotate_turret(direction)


    def update(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        directions = np.zeros(4)

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
        if keys[pygame.K_HOME]:
            self.bouncebot.reset_servo_angles()
        if keys[pygame.K_r]:
            pass
            # TODO: start / stop recording video

        self.process_directions(directions)


def main():
    # initialize bouncebot
    bb = BounceBot()

    # initialize manual controller
    mc = ManualControl(bb)

    # initialize camera
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(2)

        # main control loop
        try:
            for frame in camera.capture_continuous(rawCapture, format="bgr",
                                                   use_video_port=True):  # use_video_port=True
                # update the pygame display
                cv2.imshow("video", frame.array)  # OpenCV image show
                rawCapture.truncate(0)  # Release cache

                # control the robot
                mc.update()

                # quit on keypress
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            camera.close()
            rawCapture.close()
            pygame.quit()
            bb.close()


if __name__ == "__main__":
    main()
