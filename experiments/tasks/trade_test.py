from detectors import TaskDetector_New
from camera import Camera
from cruiser import Cruiser
import config
import time
from driver import Driver
import cv2
from cart import Cart
from widgets_servo_test import Servo_pwm, Motor_rotate, Servo
pwm2 = Servo_pwm(2)
moto1 = Motor_rotate(1)


def black_img(frame):
    frame[0:80][0:640] = 0
    frame[450:480][0:640] = 0
    return frame


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
    return frame, area, results_center

#495,411
driver = Driver()
tdn = TaskDetector_New()
cruiser = Cruiser()
cart = Cart()
front_camera = Camera(config.front_cam, [640, 480])
#side_camera = Camera(config.side_cam, [640, 480])
front_camera.start()
#side_camera.start()
time.sleep(2)
nfind_cereal_num = 0
zhuan_flag = 0
angle_pid_flag = 0
for i in range(100):
    front_image = front_camera.read()
    front_image = black_img(front_image)
    #side_image = side_camera.read()
    tasks, score = tdn.detect(front_image)
    res = driver.go(front_image)
    if abs(res) > 0.2:
        res = 0
    # driver.set_speed(10)
    find_trade_flag = 0
    if len(tasks) > 0 and score > 0.4 and tasks[0].name == 'trade':
        side_image, trade_area, trade_center = draw_res(front_image, tasks)
        find_trade_flag = 1
    if abs(res) > 0.07 and zhuan_flag == 0:
        val = 30 * res
        if val < 10:
            val = 10
        driver.cart.move([val, val, val, val])
        continue
    elif abs(res) < 0.07 and zhuan_flag == 0:
        driver.cart.move([0, 0, 0, 0])
        # time.sleep(1)
        zhuan_flag = 1
    if find_trade_flag == 1 and (abs(trade_center[1] - 411) < 5 and abs(trade_center[0] - 495) < 5) or i == 100:
        driver.cart.move([0, 0, 0, 0])
        time.sleep(1)
        driver.cart.move([10, -10, 10, -10])
        time.sleep(0.4)
        driver.cart.move([10, 10, -10, -10])
        time.sleep(1.8)
        driver.cart.move([0, 0, 0, 0])
        time.sleep(1)
        pwm2.servocontrol(70, 30)
        time.sleep(1)
        pwm2.servocontrol(0, 30)
        time.sleep(1)
        moto1.motor_rotate(-30)
        time.sleep(0.3)
        moto1.motor_rotate(0)
        time.sleep(1)
        # pwm2.servocontrol(0, 30)
        # time.sleep(1)
        pwm2.servocontrol(70, 30)
        time.sleep(1)
        moto1.motor_rotate(30)
        time.sleep(0.4)
        moto1.motor_rotate(0)
        time.sleep(10000)

    elif find_trade_flag == 1 and abs(trade_center[1] - 411) < 5 and trade_center[0] - 495 > 5:
        driver.cart.move([-10, 10, -10, 10])
        time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])
    elif find_trade_flag == 1 and abs(trade_center[1] - 411) < 5 and trade_center[0] - 495 < -5:
        driver.cart.move([10, -10, 10, -10])
        time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])
    elif find_trade_flag == 1 and trade_center[1] - 411 > 5 and abs(trade_center[0] - 495) < 5:
        driver.cart.move([-10, -10, 10, 10])
        time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])
    elif find_trade_flag == 1 and trade_center[1] - 411 > 5 and trade_center[0] - 495 > 5:
        driver.cart.move([-15, 0, 0, 15])
        time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])
    elif find_trade_flag == 1 and trade_center[1] - 411 > 5 and trade_center[0] - 495 < -5:
        driver.cart.move([0, -15, 15, 0])
        time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])
    elif find_trade_flag == 1 and trade_center[1] - 411 < -5 and abs(trade_center[0] - 495) < 5:
        driver.cart.move([10, 10, -10, -10])
        time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])
    elif find_trade_flag == 1 and trade_center[1] - 411 < -5 and trade_center[0] - 495 > 5:
        driver.cart.move([0, 15, -15, 0])
        time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])
    elif find_trade_flag == 1 and trade_center[1] - 411 < -5 and trade_center[0] - 495 < -5:
        driver.cart.move([15, 0, 0, -15])
        time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])