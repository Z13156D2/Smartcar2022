import os
import cv2
import time
from cruiser import Cruiser

from detectors import SignDetector, TaskDetector


from camera import Camera
import config
from driver import Driver

from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate

driver = Driver()
if __name__=='__main__':
    while True:
        for _ in range(18):
            driver.cart.move([-10, -10, 10, -10])