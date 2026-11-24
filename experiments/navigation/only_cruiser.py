import cv2
import time
from cruiser import Cruiser
import cruiser
from detectors import SignDetector, TaskDetector
#from detectors import TaskDetector_New
from camera import Camera
import config
from driver import Driver
from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate
pwm2 = Servo_pwm(2)
moto1 = Motor_rotate(1)

driver = Driver()
cruiser = Cruiser()
tdn = TaskDetector()
rab_pwm_servo = Servo_pwm(2)  # 夹块舵机
#led = Light(2)
image_extensions = [".png", ".jpg", ".jpeg"]
# 程序开启运行开关
start_button = Button(1, "UP")
# 程序关闭开关
stop_button = Button(1, "DOWN")
# left_button
left_button = Button(1, "LEFT")
# 保存视频标志位
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
    #frame[0:0][0:0] = 0
    frame[0:80][0:640] = 0
    frame[450:480][0:640] = 0
    return frame

i = 0

#count = 0
tower_list = [0, 0, 0, 0, 0]
target_list = [0, 0, 0, 0, 0]
cereal_list = [0, 0, 0, 0, 0]
lump_list = [0, 0, 0, 0, 0]
campsite_list = [0, 0, 0, 0, 0]
if __name__ == "__main__":
    ################
    # 摄像头初始化
    front_camera = Camera(config.front_cam, [640, 480])
    side_camera = Camera(config.side_cam, [640, 480])
    # time.sleep(3)
    front_camera.start()
    side_camera.start()
    time.sleep(3)
    # side_camera.start()
    ################
    # 舵机，电机初始化
    camera_servo = Servo(1)  # 1摄像头舵机
    # time.sleep(2)
    # camera_servo.servocontrol(124, 50)
    # time.sleep(2)
    dunhuang_servo = Servo_pwm(3)  # 敦煌旗帜
    # dunhuang_servo.servocontrol(-15, 50)  # 初始化
    daijun_servo = Servo_pwm(4)  # 代郡旗帜
    # daijun_servo.servocontrol(-5, 80)
    dingxiagn_servo = Servo_pwm(5)  # 定襄旗帜
    # dingxiagn_servo.servocontrol(-1, 80)
    rab_servo = Servo(2) # 2夹块智能舵机
    rab_pwm_servo = Servo_pwm(2) # 夹块舵机
    cereal_pwm = Servo_pwm(6) # 放球舵机
    # time.sleep(0)
    target_motor = Motor_rotate(2)
    cereal_motor = Motor_rotate(1)
    # 检测模型
    sd = SignDetector()  # 地标检测模型
    #td = TaskDetector() #侧边检测模型
    time.sleep(1)
    ################
    # 巡航参数
    car_speed = 42
    angle_pid_flag = 0
    tower_Kx = 1.0
    target_Kx = 0.92  # 0.92

    campsite_Kx = 0.89  # 0.85
    lump_Kx = 1.2  # 1.2#1.1#1.04.
    cereal_Kx = 1.02  # 0.83
    # driver.set_speed_kx = 30 #麦轮分解系数
    # driver.set_speed(35) #35#基础速度
    # driver.cart.Kx = 0.9 #0.9转向系数
    # driver.cart.speed_kx = 40
    driver.set_speed(car_speed)
    # 转弯系数
    driver.cart.Kx = tower_Kx# 0.73#1.05
    # driver.cart.speed_kx = 25
    driver.cart.slow_ratio = 1
    #############
    # while True:;
    #     if start_button.clicked():
    #         time.sleep(0.3)
    #         break
    #     print("Wait for start!")
    right_button_flag = 0
    tower_num = 0
    target_num = 0
    while True:
        front_image = front_camera.read()
        #front_image = black_img(front_image)
        if stop_button.clicked():
            driver.cart.move([0, 0, 0, 0])
            #rab_pwm_servo.servocontrol(60, 50)
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

                # print("Wait for start")
        # side_image = side_camera.read()
        res = driver.go(front_image)
        print(res)
        signs, index = sd.detect(front_image)
        sign_center = [0, 0]
        # if len(signs) > 0:
        #     frame, area, sign_center = draw_res(front_image, signs)
        #     driver.cart.steer(res)
        # else:
        #     driver.cart.steer(res)

        if len(signs) > 0 and signs[0].name == "tower":
            del (tower_list[0])
            tower_list.append(1)
            print(tower_list)
            if tower_list.count(1) > 1 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 180:
                driver.cart.Kx = tower_Kx
                #driver.cruiser.predictor.load(config.cruise["model"])
        else:
            del (tower_list[0])
            tower_list.append(0)

        if len(signs) > 0 and signs[0].name == "target":
            del (target_list[0])
            target_list.append(1)
            if target_list.count(1) > 4 and sign_center[1] > 260 and abs(sign_center[0] - 320) < 180:
                driver.cart.Kx = target_Kx
                #driver.cruiser.predictor.load(config.cruise["model"])
        else:
            del (target_list[0])
            target_list.append(0)

        if len(signs) > 0 and signs[0].name == "cereal" and area < 12000:
            del (cereal_list[0])
            cereal_list.append(1)
            if cereal_list.count(1) > 1 and area > 4500: #4500
                driver.cart.Kx = cereal_Kx
                time.sleep(0.5)
                #driver.cruiser.predictor.load(config.cruise_new["model"])
                driver.cart.move([0, 0, 0, 0])
                time.sleep(1)
                driver.cart.move([-20, -20, 20, 20])
                time.sleep(0.5)
                driver.cart.move([0, 0, 0, 0])
                time.sleep(1)
                nfind_cereal_num = 0
                zhuan_flag = 0
                angle_pid_flag = 0
                for i in range(100):
                    front_image = front_camera.read()
                    front_image = black_img(front_image)
                    side_image = side_camera.read()
                    tasks, score = tdn.detect(side_image)
                    res = driver.go(front_image)
                    if abs(res) > 0.2:
                        res = 0
                    # driver.set_speed(10)
                    find_trade_flag = 0
                    if len(tasks) > 0 and score > 0.4 and tasks[0].name == 'trade':
                        side_image, trade_area, trade_center = draw_res(side_image, tasks)
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
                    if find_trade_flag == 1 and (
                            abs(trade_center[1] - 411) < 5 and abs(trade_center[0] - 495) < 5) or i == 99:
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
                        time.sleep(1)
                        break

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


        else:
            del (cereal_list[0])
            cereal_list.append(0)

        if len(signs) > 0 and signs[0].name == "lump" and area > 3500 and area < 12000:
            del (lump_list[0])
            lump_list.append(1)
            if lump_list.count(1) > 1 and area > 6000:
                driver.cart.Kx = lump_Kx
                #driver.cruiser.predictor.load(config.cruise["model"])
        else:
            del (lump_list[0])
            lump_list.append(0)

        if len(signs) > 0 and signs[0].name == "campsite":
            del (campsite_list[0])
            campsite_list.append(1)
            if campsite_list.count(1) > 2 and area > 3500 and area < 24000 and abs(sign_center[1] - 320) < 50:
                driver.cart.Kx = campsite_Kx
                #driver.cruiser.predictor.load(config.cruise_new["model"])
        else:
            del (campsite_list[0])
            campsite_list.append(0)

        print("Kx", driver.cart.Kx)
        #count += 1
        #print(count)
    front_camera.stop()

