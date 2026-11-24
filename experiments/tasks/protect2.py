import cv2
import time
from cruiser import Cruiser
from detectors import SignDetector, Trade_two, Task_Purchase, TaskDetector
# from detectors import TaskDetector_New
from camera import Camera
import config
from driver import Driver
from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate, UltrasonicSensor
from knn import knn


def draw_res(frame, results):
    res = list(frame.shape)
    area = 0
    results_center = [0, 0]
    for item in results:
        print(item)
        left = item.relative_box[0] * res[1]
        top = item.relative_box[1] * res[0]
        right = item.relative_box[2] * res[1]
        bottom = item.relative_box[3] * res[0]
        start_point = (int(left), int(top))
        end_point = (int(right), int(bottom))
        width = end_point[0] - start_point[0]
        height = end_point[1] - start_point[1]
        # print(str(width) + 'dfas' + str(height))
        if width <= 0 or height <= 0:
            width = 0
            height = 0
        results_center[0] = int(left) + width/2
        results_center[1] = int(top) + height/2
        area = width * height
        # print("area:" + str(area))
        color = (0, 244, 10)
        thickness = 2
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = start_point[0], start_point[1] - 10
        area_org = 250, 50
        fontScale = 1
        frame = cv2.putText(frame, item.name, org, font, fontScale, color, thickness, cv2.LINE_AA)
    return frame, area, results_center, width

driver = Driver()
front_camera = Camera(config.front_cam, [640, 480])
side_camera = Camera(config.side_cam, [640, 480])
front_camera.start()
side_camera.start()
time.sleep(1)
sd = SignDetector()  # 地标检测模型
tt = Trade_two() # 侧边检测模型
td = TaskDetector()
time.sleep(1)
front_image = front_camera.read()
side_image = side_camera.read()
signs, index = sd.detect(front_image)
sign_center = [0, 0]
abc=0
# driver.cart.move([10,-10,10,-10])
while True:
    for i in range(100):
        res = driver.go(front_image)
        print(res)
        result, score = td.detect(side_image)
        frame, area, sign_center, width= draw_res(side_image, result)
        print(sign_center[0])
        print(width)
        # if sign_center[0]==0:
        #     driver.cart.move([10,-10,10,-10])
        #     time.sleep(0.8)
        if sign_center[0]!=0 and abs(res+0.41-(sign_center[0]-443)/1200) > 0.03:
            val = 30 * (res+0.41-(sign_center[0]-443)/1200)
            if val < 10 and val > 0:
                val = 10
            if val > -10 and val <= 0:
                val = -10
            driver.cart.move([val, val, val, val])
            time.sleep(0.1)
            driver.cart.move([0, 0, 0, 0])
            # driver.cart.move([10,-10,10,-10])
        elif sign_center[0]!=0 and abs(res+0.41-(sign_center[0]-443)/1200) < 0.03:
            driver.cart.move([0, 0, 0, 0])
            time.sleep(1)
# for i in range(100):
#     res = driver.go(front_image)
#     # result, score = td.detect(side_image)
#     # frame, area, sign_center = draw_res(side_image, result)
#     if abs(res + 0.55) > 0.07:
#         val = 30 * (res + 0.55)
#         if val < 10 and val > 0:
#             val = 0
#         if val > -10 and val <= 0:
#             val = -10
#         driver.cart.move([0, 0, val, val])
#         time.sleep(0.1)
#         driver.cart.move([0, 0, 0, 0])
#         continue
#     elif abs(res + 0.55) <= 0.07:
#         driver.cart.move([0, 0, 0, 0])
