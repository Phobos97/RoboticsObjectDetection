from robot_hat import Pin, PWM, Servo
from picarx import Picarx
import time


class BounceBot(Picarx):
    """
    Controller for the BounceBot.
    """
    def __init__(self):
        super().__init__()
        # initialize servo control
        self.turret_servo = Servo(PWM('P3'))
        self.turret_servo.angle(0)

        # initialize solenoid control
        self.turret_solenoid_1 = Pin("D0")
        self.turret_solenoid_2 = Pin("D1")

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

    def right_turn(self):
        pass

    def left_turn(self):
        pass

    def u_turn(self):
        pass


def test_controls():
    """
    Test the controls.
    :return:
    """
    bb = BounceBot()

    try:    # use try/finally to ensure the motors and solenoid are turned off
        # drive and steer
        bb.forward(30)
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
            bb.set_camera_servo1_angle(angle)
            time.sleep(0.01)
        for angle in range(35, -35, -1):
            bb.set_camera_servo1_angle(angle)
            time.sleep(0.01)
        for angle in range(-35, 0):
            bb.set_camera_servo1_angle(angle)
            time.sleep(0.01)
        for angle in range(0, 35):
            bb.set_camera_servo2_angle(angle)
            time.sleep(0.01)
        for angle in range(35, -35, -1):
            bb.set_camera_servo2_angle(angle)
            time.sleep(0.01)
        for angle in range(-35, 0):
            bb.set_camera_servo2_angle(angle)
            time.sleep(0.01)

        # test turret
        for a in (0, 70, 0, -70):
            bb.turret_servo.angle(a)
            time.sleep(0.5)
            bb.activate_solenoid(0.2)
            time.sleep(0.5)

    finally:
        bb.activate_solenoid(0.1)
        bb.forward(0)


if __name__ == "__main__":
    test_controls()
