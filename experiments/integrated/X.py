import time
import cv2
import config
from camera import Camera
from driver import Driver, SLOW_DOWN_RATE
from detectors import SignDetector, TaskDetector
from cruiser import Cruiser
from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate

cruiser = Cruiser()
driver = Driver()
led = Light(2)
# 保存视频标志位
save_video_flag = 0
# 保存图片标注位
save_image_flag = 0
# 程序开启运行开关
start_button = Button(1, "UP")

target_list = [0, 0, 0, 0, 0]

def draw_res(frame, results, btn):
    res = list(frame.shape)  # 转化为列表  应该是[480, 480, 3]
    area = 0
    results_center = [0, 0]
    for item in results:
        left = item.relative_box[0] * res[1]  # res[0]为480，res[1]为640
        top = item.relative_box[1] * res[0]  # relative_box[0];[1];[2];[3]是检测到目标的位置信息
        right = item.relative_box[2] * res[1]
        bottom = item.relative_box[3] * res[0]
        start_point = (int(left), int(top))
        end_point = (int(right), int(bottom))
        width = end_point[0] - start_point[0]
        height = end_point[1] - start_point[1]
        if width <= 0 or height <= 0:  # 当目标的下边线无法检测时
            width = 0
            height = 0
        results_center[0] = int(left) + width/2
        results_center[1] = int(top) + height/2
        area = width * height  # 面积
        color = (0, 244, 10)
        thickness = 2
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = start_point[0], start_point[1] - 10
        area_org = 250, 50
        fontScale = 1
        frame = cv2.putText(frame, item.name, org, font, fontScale, color, thickness, cv2.LINE_AA)
        file = "/home/root/workspace/autostart/src/image/picture"
        picture_path = "{}/{}.png".format(file, btn)
        cv2.imwrite(picture_path, frame)
    return frame, area, results_center  # 返回画框后的图片，面积和中心点

def black_img(frame):
    frame[0:120][0:640] = 0
    frame[400:480][0:640] = 0
    return frame
btn = 0

if __name__ == "__main__":
    #rab_servo = Servo(2)  # 2夹块智能舵机
    rab_pwm_servo = Servo_pwm(2)  # 夹块舵机
    time.sleep(1)
    rab_pwm_servo.servocontrol(80, 50)
    time.sleep(1)
    rab_pwm_servo.servocontrol(120, 50)
    time.sleep(1)
    # rab_pwm_servo.servocontrol(120, 50)
    # time.sleep(0.5)
    # rab_servo.servocontrol(80, 60)
    # time.sleep(1)
    # rab_pwm_servo.servocontrol(12, 50)
    # time.sleep(0.5)
    # rab_servo.servocontrol(15, 80)
    # time.sleep(1)
    ###############
    # 初始化
    '''front_camera = Camera(config.front_cam, [640, 400])
    side_camera = Camera(config.side_cam, [640, 480])  # 行的长度640，列的宽度480
    front_camera.start()
    side_camera.start()
    time.sleep(3)
    sd = SignDetector()
    time.sleep(1)
    camera_servo = Servo(1)  # 摄像头舵机
    dunhuang_servo = Servo_pwm(3)  # 敦煌旗帜
    daijun_servo = Servo_pwm(4)  # 代郡旗帜
    dingxiagn_servo = Servo_pwm(5)  # 定襄旗帜
    target_motor = Motor_rotate(2)
    cereal_motor = Motor_rotate(1)
    rab_pwm_servo = Servo_pwm(2)  # 夹块舵机
    rab_servo = Servo(2)  # 2夹块智能舵
    ###############
    # 巡航参数
    car_speed = 45
    driver.set_speed(car_speed)
    right_button_flag = 0
    tower_num = 0
    target_num = 0
    target_Kx = 0.82
    tower_list = [0, 0, 0, 0, 0]
    tower_Kx = 0.86
    sd = SignDetector()  # 地标检测模型
    td = TaskDetector()  # 侧边检测模型
    while True:
        if start_button.clicked():
            time.sleep(0.3)
            rab_pwm_servo.servocontrol(60, 50)
            time.sleep(0.3)
            rab_pwm_servo.servocontrol(63, 50)
            time.sleep(0.3)
            rab_servo.servocontrol(23, 60)
            time.sleep(0.3)
            break
        print("Wait for start!")
    while True:
        front_image = front_camera.read()
        front_image = black_img(front_image)
        driver.set_speed(car_speed)  # 设定初始值
        driver.cart.Kx = tower_Kx  # 转弯系数
        driver.cart.slow_ratio = 1
        res = driver.go(front_image)  # 对front图片预测并输出res(偏差)
        print(res)
        signs, index = sd.detect(front_image)
        sign_center = [0, 0]
        if len(signs) > 0:
            btn += 1
            frame, area, sign_center = draw_res(front_image, signs, btn)
            driver.cart.steer(res)
        else:
            driver.cart.steer(res)
        ###############
        # 识别城堡并举旗
        if len(signs) > 0 and signs[0].name == "tower":
            if sign_center[1] > 300 and abs(sign_center[0] - 320) < 180:  # TODO
                time.sleep(0.42)
                driver.cart.move([0, 0, 0, 0])
                tower_num += 1
                print(tower_num)
                if tower_num == 1 or tower_num == 3:
                    camera_servo.servocontrol(124, 50)
                elif tower_num == 2:
                    camera_servo.servocontrol(-40, 50)  # 识别标志到停止
                time.sleep(1)
                find_tower_frame_num = 0
                find_tower_flag = 0
                tasks = [0, 0]
                forward = 0
                backward = 0
                for i in range(30):
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    if len(tasks) > 0 and score > 0.75 and(tasks[0].name == "daijun" or tasks[0].name == "dunhuang" or tasks[0].name == "dingxiang"):
                        btn += 1
                        draw_res(side_image, tasks, btn)
                        find_tower_frame_num += 1
                    if find_tower_frame_num >= 3:
                        find_tower_flag = 1
                        if forward == 1:
                            driver.cart.move([10, -10, 10, 10])  # 前进
                            time.sleep(1.3)
                            driver.cart.move([0, 0, 0, 0])
                            forward = 0
                        if backward == 1:
                            driver.cart.move([-10, 10, -10, 10])  # 后退
                            time.sleep(1.3)
                            driver.cart.move([0, 0, 0, 0])
                            backward = 0
                        break
                    if i == 10:
                        driver.cart.move([10, -10, 10, -10])
                        time.sleep(1.3)
                        driver.cart.move([0, 0, 0, 0])
                        backward = 1
                    if i == 20:
                        driver.cart.move([10, -10, 10, -10])
                        time.sleep(1.3)
                        driver.cart.move([0, 0, 0, 0])
                        forward = 1
                if forward == 1:
                    forward = 0
                    driver.cart.move([-10, 10, -10, 10])
                    time.sleep(1.3)
                    driver.cart.move([0, 0, 0, 0])
                if backward == 1:
                    backward = 0
                    driver.cart.move([10, -10, 10, -10])
                    time.sleep(1.3)
                    driver.cart.move([0, 0, 0, 0])
                driver.cart.Kx = tower_Kx
                if len(tasks) > 0 and tasks[0].name == "dunhuang":
                    print(tasks[0].name)
                    dunhuang_servo.servocontrol(85, 50)
                    time.sleep(0.1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        led.lightoff()
                    dunhuang_servo.servocontrol(-15, 50)
                elif len(tasks) > 0 and tasks[0].name == "daijun":
                    print("tasks[0].name=", tasks[0].name)
                    daijun_servo.servocontrol(45, 80)
                    time.sleep(0.1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        led.lightoff()
                    daijun_servo.servocontrol(-5, 50)
                elif len(tasks) > 0 and tasks[0].name == "dingxiang":
                    print(tasks[0].name)
                    dingxiagn_servo.servocontrol(45, 80)
                    time.sleep(0.1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        led.lightoff()
                    dingxiagn_servo.servocontrol(-1, 80)


        # 打靶
        if len(signs) > 0 and signs[0].name == "target":
            if sign_center[1] > 300 and abs(sign_center[0] - 320) < 180:
                driver.cart.Kx = target_Kx
                # time.sleep(0.42)
                driver.cart.move([0, 0, 0, 0])
                camera_servo.servocontrol(-40, 50)
                time.sleep(1)
                nfind_target_flag = 0
                find_target_flag = 1
                zhuan_flag = 0
                x1_flag = 0
                for i in range(80):
                    front_image = front_camera.read()
                    front_image = black_img(front_image)
                    res = driver.go(front_image)
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    print(res)
                    if res > 0.25:
                        res = 0.05
                    elif res < -0.25:
                        res = -0.05
                    if len(tasks) > 0 and score > 0.5 and tasks[0].name == "red_target":
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        find_target_flag = 1
                    elif len(tasks) == 0 and zhuan_flag == 1:
                        driver.cart.move([-10, 10, -10, 10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        nfind_target_flag += 1

                    if abs(res) > 0.02 and zhuan_flag == 0:
                        val = 30 * res
                        if val < 10:
                            val = 10
                        elif val > 25:
                            val = 10
                        driver.cart.move([val, val, val, val])  # 调整车姿
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        continue
                    elif abs(res) < 0.02 and zhuan_flag == 0:
                        driver.cart.move([15, -15, 15, -15])  # 前进
                        time.sleep(1.8)
                        driver.cart.move([0, 0, 0, 0])
                        zhuan_flag = 1

                    if find_target_flag == 1 and abs(target_center[1] - 200) < 15 and x1_flag == 0:
                        x1_flag = 1
                    elif find_target_flag == 1 and target_center[1] - 200 > 15 and x1_flag == 0:
                        driver.cart.move([-20, -20, 20, 20])  # 远离
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_target_flag == 1 and target_center[1] - 200 < -15 and x1_flag == 0:
                        driver.cart.move([20, 20, -20, -20])  # 靠近
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    if (find_target_flag == 1 and x1_flag == 1 and abs(int(target_center[0]) - 295) < 1 and zhuan_flag) or i == 79 or nfind_target_flag == 5:
                        print(nfind_target_flag)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        target_motor.motor_rotate(-40)  # 打靶
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
                    elif find_target_flag == 1 and x1_flag == 1 and (
                            int(target_center[0]) - 295) > 1 and zhuan_flag:
                        driver.cart.move([-8, 8, -8, 8])  # 向前
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_target_flag == 1 and x1_flag == 1 and (
                            int(target_center[0]) - 295) < -1 and zhuan_flag:
                        driver.cart.move([8, -8, 8, -8])  # 向后
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])


        # 物块
        if len(signs) > 0 and signs[0].name == "lump":
            time.sleep(1)
            camera_servo.servocontrol(124, 50)
            side_image = side_camera.read()
            tasks, score = td.detect(side_image)
            btn += 1
            side_image, target_area, target_center = draw_res(side_image, tasks, btn)'''



