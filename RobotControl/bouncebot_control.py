from robot_hat import Pin, PWM, Servo
from picarx import Picarx
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np


class BounceBot(Picarx):
    """
    Controller for the BounceBot.
    """

    def __init__(self):
        super().__init__()
        # initialize servo control
        self.turret_servo = Servo(PWM('P3'))

        # initialize solenoid control
        self.turret_solenoid_1 = Pin("D0")
        self.turret_solenoid_2 = Pin("D1")

        # parameters
        self.max_speed = 50

        self.dir_servo_current_angle = 0
        self.dir_servo_max_angle = 40
        self.dir_servo_angular_speed = 3  # deg / frame

        self.camera_servo1_current_angle = 0
        self.camera_servo1_max_angle = 60
        self.camera_servo1_angular_speed = 3  # deg / frame

        self.camera_servo2_current_angle = 0
        self.camera_servo2_max_angle = 35
        self.camera_servo2_angular_speed = 3  # deg / frame

        self.turret_servo_current_angle = 0
        self.turret_servo_max_angle = 35
        self.turret_servo_angular_speed = 3  # deg / frame

        # set all servo angles to 0
        self.set_camera_bottom_servo_angle(0)
        self.set_camera_top_servo_angle(0)
        self.set_turret_servo_angle(0)
        self.set_direction_servo_angle(0)

    def reset_servo_angles(self):
        self.set_camera_bottom_servo_angle(0)
        self.set_camera_top_servo_angle(0)
        self.set_turret_servo_angle(0)
        self.set_direction_servo_angle(0)
        self.dir_servo_current_angle = 0
        self.camera_servo1_current_angle = 0
        self.camera_servo2_current_angle = 0
        self.turret_servo_current_angle = 0

    def close(self):
        self.turret_solenoid_1.value(0)
        self.turret_solenoid_2.value(0)
        self.forward(0)
        self.reset_servo_angles()

    def activate_solenoid(self, t):
        """
        Activate the solenoid for a certain amount of time t.
        :param t: time in seconds
        :return:
        """
        self.turret_solenoid_1.value(1)
        self.turret_solenoid_2.value(1)
        time.sleep(t)
        self.turret_solenoid_1.value(0)
        self.turret_solenoid_2.value(0)

    def set_camera_bottom_servo_angle(self, angle):
        self.set_camera_servo1_angle(
            np.clip(angle, -self.camera_servo1_max_angle, self.camera_servo1_max_angle, dtype=float)
        )

    def set_camera_top_servo_angle(self, angle):
        self.set_camera_servo2_angle(
            np.clip(angle, -self.camera_servo2_max_angle, self.camera_servo2_max_angle, dtype=float)
        )

    def set_turret_servo_angle(self, angle):
        self.turret_servo.angle(
            np.clip(angle, -self.turret_servo_max_angle, self.turret_servo_max_angle, dtype=float)
        )

    def set_direction_servo_angle(self, angle):
        self.dir_servo_current_angle = np.clip(
            angle, -self.dir_servo_max_angle, self.dir_servo_max_angle, dtype=float
        )
        self.set_dir_servo_angle(self.dir_servo_current_angle)

    # functions for manual control
    def look_horizontal(self, direction):
        if direction == 1:
            self.camera_servo1_current_angle += self.camera_servo1_angular_speed
        elif direction == -1:
            self.camera_servo1_current_angle -= self.camera_servo1_angular_speed
        self.set_camera_bottom_servo_angle(self.camera_servo1_current_angle)

    def look_vertical(self, direction):
        if direction == 1:
            self.camera_servo2_current_angle += self.camera_servo2_angular_speed
        elif direction == -1:
            self.camera_servo2_current_angle -= self.camera_servo2_angular_speed
        self.set_camera_top_servo_angle(self.camera_servo2_current_angle)

    def turn(self, direction):
        if direction == 1:
            self.dir_servo_current_angle += self.dir_servo_angular_speed
        elif direction == -1:
            self.dir_servo_current_angle -= self.dir_servo_angular_speed
        elif direction == 0:
            if self.dir_servo_current_angle > 0:
                self.dir_servo_current_angle -= self.dir_servo_angular_speed
            elif self.dir_servo_current_angle < 0:
                self.dir_servo_current_angle += self.dir_servo_angular_speed
        self.set_direction_servo_angle(self.dir_servo_current_angle)

    def move(self, speed):
        move_speed = np.clip(speed, -self.max_speed, self.max_speed, dtype=float)

        if move_speed >= 0:
            self.forward(move_speed)
        elif move_speed < 0:
            self.backward(-move_speed)

    def rotate_turret(self, direction):
        if direction == 1:
            self.turret_servo_current_angle += self.turret_servo_angular_speed
        elif direction == -1:
            self.turret_servo_current_angle -= self.turret_servo_angular_speed
        self.set_turret_servo_angle(self.turret_servo_current_angle)

    def turn_90(self, direction='right'):
        """
        Stops and turns the robot right or left by 90 degrees.

        If the robot is faced in the x direction, it will turn to the y direction.
        It moves an additional +/- 8 cm in the x direction.
        It moves an additional +/- 38 cm in the y direction.
        :return:
        """

        if direction == 'right':
            angle = 30
        elif direction == 'left':
            angle = -30
        else:
            raise ValueError('direction must be either "right" or "left"')

        self.move(0)
        self.set_direction_servo_angle(angle)
        time.sleep(1)
        self.move(1)
        time.sleep(1.4)
        self.move(0)
        self.set_direction_servo_angle(0)
        time.sleep(0.5)

    def turn_270(self, direction='right'):
        """
        Stops and turns the robot by right by rotating 270 degrees left.

        It will first move forward and then turn left.
        It will stop approximately at the position it started, only rotated right by 90 degrees.
        :return:
        """

        if direction == 'right':
            angle = -30
        elif direction == 'left':
            angle = 30
        else:
            raise ValueError('direction must be either "right" or "left"')

        self.move(0)
        time.sleep(0.5)
        self.move(1)
        time.sleep(1.25)
        self.move(0)
        time.sleep(0.5)
        self.set_direction_servo_angle(angle)
        time.sleep(1)
        self.move(1)
        time.sleep(3.9)
        self.move(0)
        self.set_direction_servo_angle(0)
        time.sleep(0.5)
        self.move(1)
        time.sleep(0.2)
        self.move(0)
        time.sleep(0.5)

    def u_turn(self, direction='right'):
        if direction == 'right':
            angle = -30
        elif direction == 'left':
            angle = 30
        else:
            raise ValueError('direction must be either "right" or "left"')

        self.turn_90(direction)
        self.move(0)
        self.set_direction_servo_angle(angle)
        time.sleep(1)
        self.move(1)
        time.sleep(4.0)
        self.move(0)
        self.set_direction_servo_angle(0)
        time.sleep(0.5)
        self.move(1)
        time.sleep(0.6)
        self.move(0)
        time.sleep(0.5)

    def around_obstacle(self, direction='right'):
        """
        Turn around the box when it is at 25cm from the front of the robot.
        :param direction:
        :return:
        """

        if direction == 'right':
            dir_mod = 1
        elif direction == 'left':
            dir_mod = -1
        else:
            raise ValueError('direction must be either "right" or "left"')

        self.move(0)
        self.set_direction_servo_angle(dir_mod * 15)
        time.sleep(0.5)
        self.move(1)
        time.sleep(1)
        self.move(0)

        self.set_direction_servo_angle(dir_mod * -30)
        time.sleep(0.5)
        self.move(1)
        time.sleep(1.3)
        self.move(0)

        self.set_direction_servo_angle(dir_mod * 35)
        time.sleep(0.5)
        self.move(1)
        time.sleep(0.7)
        self.move(0)

        self.move(0)
        self.set_direction_servo_angle(0)


def test_controls():
    """
    Test the controls.
    :return:
    """
    bb = BounceBot()

    try:  # use try/finally to ensure the motors and solenoid are turned off
        # drive and steer
        bb.move(30)
        time.sleep(0.5)
        for angle in range(0, 35):
            bb.set_dir_servo_angle(angle)
            time.sleep(0.01)
        for angle in range(35, -35, -1):
            bb.set_dir_servo_angle(angle)
            time.sleep(0.01)
        for angle in range(-35, 0):
            bb.set_dir_servo_angle(angle)
            time.sleep(0.01)
        bb.forward(0)
        time.sleep(1)

        # look with camera
        for angle in range(0, 35):
            bb.set_camera_bottom_servo_angle(angle)
            time.sleep(0.01)
        for angle in range(35, -35, -1):
            bb.set_camera_bottom_servo_angle(angle)
            time.sleep(0.01)
        for angle in range(-35, 0):
            bb.set_camera_bottom_servo_angle(angle)
            time.sleep(0.01)
        for angle in range(0, 35):
            bb.set_camera_top_servo_angle(angle)
            time.sleep(0.01)
        for angle in range(35, -35, -1):
            bb.set_camera_top_servo_angle(angle)
            time.sleep(0.01)
        for angle in range(-35, 0):
            bb.set_camera_top_servo_angle(angle)
            time.sleep(0.01)

        # test turret
        for a in (0, 70, 0, -70):
            bb.set_turret_servo_angle(a)
            time.sleep(0.5)
            bb.activate_solenoid(0.2)
            time.sleep(0.5)

    finally:
        bb.close()


if __name__ == "__main__":
    test_controls()
