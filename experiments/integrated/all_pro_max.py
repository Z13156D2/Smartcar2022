import cv2
import time
from detectors import SignDetector
from detectors import TaskDetector
from camera import Camera
import config
from cruiser import Cruiser
from driver import Driver
from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate

driver = Driver
cruiser = Cruiser
led = Light(2)
image_extensions = [".png", ".jpg", ".jpeg"]
# 程序开启运行开关
start_button = Button(1, "UP")
# 程序关闭开关
stop_button = Button(1, "DOWN")
# left_button
left_button = Button(1, "LEFT")
save_video_flag = 0
# 保存图片标注位
save_image_flag = 0
image_num = 10916
image_dir = "/run/media/sda1/front720"


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
    frame[0:120][0:640] = 0
    frame[400:480][0:640] = 0
    return frame


tower_list = [0, 0, 0, 0, 0]
target_list = [0, 0, 0, 0, 0]
cereal_list = [0, 0, 0, 0, 0]
lump_list = [0, 0, 0, 0, 0]
campsite_list = [0, 0, 0, 0, 0]


if __name__ == "__main__":
    # 摄像头初始化
    front_camera = Camera(config.front_cam, [640, 480])
    side_camera = Camera(config.side_cam, [640, 480])
    front_camera.start()
    side_camera.start()
    time.sleep(3)
    # 舵机，电机初始化
    camera_servo = Servo(1)  # 1摄像头舵机
    # time.sleep(2)
    #camera_servo.servocontrol(124, 50)
    #time.sleep(2)
    dunhuang_servo = Servo_pwm(3)  # 敦煌旗帜
    #dunhuang_servo.servocontrol(-15, 50)  # 初始化
    daijun_servo = Servo_pwm(4)  # 代郡旗帜
    #daijun_servo.servocontrol(-5, 80)
    dingxiagn_servo = Servo_pwm(5)  # 定襄旗帜
    #dingxiagn_servo.servocontrol(-1, 80)
    rab_servo = Servo(2) #2夹块智能舵机
    rab_pwm_servo = Servo_pwm(2) #夹块舵机
    cereal_pwm = Servo_pwm(6) #放球舵机
    # time.sleep(0)
    target_motor = Motor_rotate(2)
    cereal_motor = Motor_rotate(1)
    # 检测模型
    sd = SignDetector()  # 地标检测模型
    # td = TaskDetector() #侧边检测模型
    time.sleep(1)
    #巡航参数
    car_speed = 45
    angle_pid_flag = 0
    tower_Kx = 0.86
    target_Kx = 0.82  # 0.92
    campsite_Kx = 0.89   # 0.85
    lump_Kx = 1.0  # 1.2#1.1#1.04
    cereal_Kx = 0.86  # 0.83
    #driver.set_speed_kx = 30 #麦轮分解系数
    #driver.set_speed(35) #35#基础速度
    #driver.cart.Kx = 0.9 #0.9转向系数
    #driver.cart.speed_kx = 40
    driver.set_speed(car_speed)
    # 转弯系数
    driver.cart.Kx = tower_Kx#0.73#1.05
    #driver.cart.speed_kx = 25
    driver.cart.slow_ratio = 1
    #############
    #保存视频
    if save_video_flag == 1:
        save_video = cv2.VideoWriter('/run/media/sda1/video/output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 6.0, (640, 480))
    while True:
        if start_button.clicked():
            time.sleep(0.3)
            break
        print("Wait for start!")
    right_button_flag = 0
    tower_num = 0
    target_num = 0
    while True:
        front_image = front_camera.read()
        front_image = black_img(front_image)
        if stop_button.clicked():
            driver.cart.move([0, 0, 0, 0])
            rab_pwm_servo.servocontrol(60, 50)
            tower_num = 0
            target_num = 0
            while True:
                if start_button.clicked():
                    driver.set_speed(car_speed)
                    # 转弯系数
                    driver.cart.Kx = tower_Kx # 1.05
                    # driver.cart.speed_kx = 25
                    driver.cart.slow_ratio = 1
                    time.sleep(0.3)
                    break
        if save_image_flag == 1:
            path = "{}/{}.jpg".format(image_dir, image_num)
            cv2.imwrite(path, front_image)
            cv2.waitKey(60)
            print(image_num)
            image_num += 1
            continue
        res = driver.go(front_image)
        if angle_pid_flag == 1:
            if res > 0.65:
                res = res - (res - 0.65) * 0.5
            elif res < -0.55:
                res = res - (res + 0.65) * 0.5
        else:
            res = res

        signs, index = sd.detect(front_image)
        sign_center = [0, 0]
        if len(signs) > 0:
            frame, area, sign_center = draw_res(front_image, signs)
            #print(area)
            #print(sign_center)
            driver.cart.steer(res)
            #if signs[0].name == 'campsite':
            #    driver.cart.Kx = 1.1
        else:
            driver.cart.steer(res)
        # 打把
        if len(signs) > 0 and signs[0].name == "target":
            del (target_list[0])
            target_list.append(1)
            if target_list.count(1) > 1 and sign_center[1] > 260 and abs(sign_center[0] - 320) < 180: #230and abs(res) < 0.1 and area > 5500:
                # time.sleep(0.35)
                # print(target_list)
                driver.cart.Kx = target_Kx
                angle_pid_flag = 0
                driver.cart.move([0, 0, 0, 0]) #    停车
                td = TaskDetector()  # 侧边检测模型
                # side_camera = Camera(config.side_cam, [640, 480])
                # side_camera.start()
                camera_servo.servocontrol(-40, 50)
                time.sleep(1)
                zhuan_flag = 0
                x1_flag = 0
                # while True:
                # target_center_list = [0, 0, 0, 0, 0]
                last_target_center = [0, 0]
                last_last_target_center = [0, 0]
                target_center = [0, 0]
                nfind_target_flag = 0
                for i in range(80):
                    front_image = front_camera.read()
                    front_image = black_img(front_image)
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    res = driver.go(front_image)
                    print("res:", res)
                    if res > 0.25:
                        res = 0.05
                    elif res < -0.25:
                        res = -0.05
                    # driver.set_speed(10)
                    find_target_flag = 0
                    target_center_x = 0
                    if len(tasks) > 0 and score > 0.5 and tasks[0].name == 'red_target':
                        # 添加
                        last_last_target_center[0] = last_target_center[0]
                        last_target_center[0] = target_center[0]

                        side_image, target_area, target_center = draw_res(side_image, tasks)
                        nfind_target_flag = 0
                        print("target_center = ", target_center)

                        if last_target_center[0] == 0 and last_last_target_center[0] != 0:
                            target_center_x = (target_center[0] + last_last_target_center[0]) / 2
                        elif last_target_center[0] != 0 and last_last_target_center[0] == 0:
                            target_center_x = (target_center[0] + last_target_center[0]) / 2
                        elif last_target_center[0] != 0 and last_last_target_center[0] != 0:
                            target_center_x = (target_center[0] + + last_last_target_center[0] + last_target_center[0]) / 3
                        elif last_target_center[0] == 0 and last_last_target_center[0] == 0:
                            target_center_x = target_center[0]
                        find_target_flag = 1
                    elif len(tasks) == 0 and zhuan_flag == 1:
                        driver.cart.move([-10, 10, -10, 10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        nfind_target_flag += 1

                    if target_num == 0:
                        if abs(res-0.05) > 0.02 and zhuan_flag == 0:
                            val = 30 * res
                            if val < 10:
                                val = 10
                            elif val > 25:
                                val = 10
                            driver.cart.move([val, val, val, val])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                            continue
                        elif abs(res-0.05) < 0.02 and zhuan_flag == 0:
                            driver.cart.move([15, -15, 15, -15])
                            time.sleep(1.8)
                            driver.cart.move([0, 0, 0, 0])
                            #time.sleep(1)`
                            zhuan_flag = 1

                    if target_num == 1:
                        if abs(res-0.40) > 0.02 and zhuan_flag == 0:
                            val = 30 * res
                            if val < 10:
                                val = 10
                            elif val > 25:
                                val = 10
                            driver.cart.move([val, val, val, val])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                            continue
                        elif abs(res-0.40) < 0.02 and zhuan_flag == 0:
                            driver.cart.move([15, -15, 15, -15])
                            time.sleep(1.8)
                            driver.cart.move([0, 0, 0, 0])
                            #time.sleep(1)`
                            zhuan_flag = 1

                    if target_num == 2:
                        if abs(res) > 0.02 and zhuan_flag == 0:
                            val = 30 * res
                            if val < 10:
                                val = 10
                            elif val > 25:
                                val = 10
                            driver.cart.move([val, val, val, val])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                            continue
                        elif abs(res) < 0.02 and zhuan_flag == 0:
                            driver.cart.move([15, -15, 15, -15])
                            time.sleep(1.8)
                            driver.cart.move([0, 0, 0, 0])
                            #time.sleep(1)`
                            zhuan_flag = 1


                    if find_target_flag == 1 and abs(target_center[1] - 200) < 15 and x1_flag == 0:
                        x1_flag = 1
                    elif find_target_flag == 1 and target_center[1] - 200 > 15 and x1_flag == 0:
                        driver.cart.move([-20, -20, 20, 20])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_target_flag == 1 and target_center[1] - 200 < -15 and x1_flag == 0:
                        driver.cart.move([20, 20, -20, -20])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])

                    if (find_target_flag == 1 and x1_flag == 1 and abs(int(target_center[0]) - 295) < 1 and zhuan_flag) or i == 79 or nfind_target_flag == 5:
                        #print("iiiiiiiiiiiii=== ", i)
                        print(nfind_target_flag)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        target_motor.motor_rotate(-40)
                        time.sleep(0.5)
                        target_motor.motor_rotate(0)
                        time.sleep(0.5)
                        target_motor.motor_rotate(15)
                        time.sleep(3.2)
                        target_motor.motor_rotate(0)
                        time.sleep(1)
                        driver.cart.move([-10, -10, 10, 10])
                        time.sleep(0.4)
                        driver.cart.move([0, 0, 0, 0])
                        target_num += 1
                        driver.set_speed(car_speed)
                        break
                    elif find_target_flag == 1 and x1_flag == 1 and (int(target_center[0]) - 295) > 1 and zhuan_flag:
                        driver.cart.move([-8, 8, -8, 8])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_target_flag == 1 and x1_flag == 1 and (int(target_center[0]) - 295) < -1 and zhuan_flag:
                        driver.cart.move([8, -8, 8, -8])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
        else:
            del (target_list[0])
            target_list.append(0)

    front_camera.stop()