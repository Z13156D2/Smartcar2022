from knn import knn
import cv2
import time
from cruiser import Cruiser
from detectors import SignDetector, Trade_two, Task_Purchase, TaskDetector
#from detectors import TaskDetector_New
from camera import Camera
import config
from driver import Driver
from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate, UltrasonicSensor
# pwm2 = Servo_pwm(2)
moto1 = Motor_rotate(1)
servo1 = Servo(1)
# led = Light(2)
driver = Driver()
cruiser = Cruiser()
#rab_pwm_servo = Servo_pwm(2)  # 夹块舵机
#led = Light(2)
image_extensions = [".png", ".jpg", ".jpeg"]
# 程序开启运行开关
# start_button = Button(1, "UP")
# # 程序关闭开关
# stop_button = Button(1, "DOWN")
# # left_button
# left_button = Button(1, "LEFT")
# 保存视频标志位
save_video_flag = 0
pwm3 = Servo_pwm(3)
# 保存图片标注位
save_image_flag = 0
image_num = 10916
pwm2 = Servo_pwm(2)
image_dir = "/run/media/sda1/front720"

trade_up_center = [280.0, 285.0]#[323.0, 345.0]
trade_down_center = [285.0, 425.0]#[327.0, 345.0]
perchase_center_right =[203.0, 430.0]# [203.0, 430.0]
fanwei_up = 315.0#275.0
fanwei_down = 320.0#285.0
up_or_down_flag = 0
#150-280
#280-380

# up 160--320
# down 315-422


def draw_cruise_result(frame, res):
    color = (0, 244, 10)
    thickness = 2

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = 450, 50

    fontScale = 1
    txt = "{:.4f}".format(round(res, 5))
    frame = cv2.putText(frame, txt, org, font,
                       fontScale, color, thickness, cv2.LINE_AA)
    # print("angle=",txt)
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


def black_img(frame):
    #frame[0:80][0:640] = 0
    frame[465:480][0:640] = 0
    return frame

i = 0

#count = 0
tower_list = [0, 0, 0, 0, 0]
protect_list = [0, 0, 0, 0, 0]
trade_list = [0, 0, 0, 0, 0]
purchase_list = [0, 0, 0, 0, 0]
campsite_list = [0, 0, 0, 0, 0]

if __name__ == "__main__":
    ################
    # 摄像头初始化
    front_camera = Camera(config.front_cam, [640, 480])
    side_camera = Camera(config.side_cam, [640, 480])
    # time.sleep(3)
    front_camera.start()
    side_camera.start()
    time.sleep(1)
    sd = SignDetector()  # 地标检测模型
    tt = Trade_two() #侧边检测模型
    time.sleep(1)
    ################
    # 巡航参数
    car_speed = 30#40
    tower_speed_1 = 45
    tower_speed_2 = 48
    tower_speed_3 = 35
    protect_speed_1 = 38
    protect_speed_2 = 42
    protect_speed_3 = 45
    protect_speed_4 = 55
    campsite_speed = 42
    purchase_speed = 45
    trade_speed = 52


    first_Kx = 1.02

    tower_Kx_1 = 0.92
    tower_Kx_2 = 1.0
    tower_Kx_3 = 1.05
    protect_Kx_1 = 1.0  # 0.92
    protect_Kx_2 = 0.92#1.0
    protect_Kx_3 = 1.05
    protect_Kx_4 = 0.9

    purchase_Kx = 1.0
    campsite_Kx = 0.93#1.0
    trade_Kx = 0.9  # 1.2#1.1#1.04.

    angle_pid_flag = 0
    find_trade_flag = 0
    driver.set_speed(car_speed)
    # 转弯系数
    driver.cart.Kx = first_Kx# 0.73#1.05
    # driver.cart.speed_kx = 25
    driver.cart.slow_ratio = 0.96
    #############
    # while True:;
    #     if start_button.clicked():
    #         time.sleep(0.3)
    #         break
    #     print("Wait for start!")
    pwm2 = Servo_pwm(2)
    right_button_flag = 0
    tower_num = 1
    protect_num = 1
    up_or_down = -1
    find_perchase_flag = 0
    td = TaskDetector()
    uls = UltrasonicSensor(4)
    asdsdsdd = 0
    move_flag = 0
    while True:
        front_image = front_camera.read()
        side_image = side_camera.read()
        res = driver.go(front_image)
        print(res)
        signs, index = sd.detect(front_image)
        #sign_center = [0, 0]
        result, score = td.detect(side_image)
        frame, area, sign_center = draw_res(side_image, result)
        if len(result) > 0:
            if result[0].name == 'badperson' or result[0].name == 'badperson2' or result[0].name == 'goodperson' or result[0].name == 'goodperson2':
                if sign_center[0] - 312 < -5:
                    driver.cart.move([-10, 10, -10, 10])
                    time.sleep(0.07)
                    driver.cart.move([0, 0, 0, 0])
                if sign_center[0] - 312 > 5:
                    driver.cart.move([10, -10, 10, -10])
                    time.sleep(0.07)
                    driver.cart.move([0, 0, 0, 0])
                if abs(sign_center[0] - 312) < 5:
                    asdsdsdd = asdsdsdd+1
            if asdsdsdd > 5:
                if move_flag == 0:
                    driver.cart.move([-10, 10, -10, 10])
                    time.sleep(0.8)
                    driver.cart.move([0, 0, 0, 0])
                    move_flag = 1
                uls1 = uls.read()
                print(uls1)





