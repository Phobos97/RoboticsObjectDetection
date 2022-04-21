from robot_hat import Pin, PWM, Servo
from picarx import Picarx
import time

px = Picarx()
servo_pin = PWM('P3')
sol_pin_a = Pin("D0")
sol_pin_b = Pin("D1")  # one pin does not supply enough current, always use both

for a in (0, 70, 0, -70):
    Servo(servo_pin).angle(a)
    time.sleep(0.3)
    sol_pin_a.value(1)
    sol_pin_b.value(1)
    time.sleep(0.2)
    sol_pin_a.value(0)
    sol_pin_b.value(0)
    time.sleep(0.5)
