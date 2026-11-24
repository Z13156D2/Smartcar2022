import sys
import datetime
import time
import cv2
import config
from widgets import Button, Light
from camera import Camera
from driver import Driver, SLOW_DOWN_RATE
from detectors import SignDetector,TaskDetector
from cruiser import Cruiser
from widgets import Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate

cruiser = Cruiser()
driver = Driver()
led = Light(2)
# 保存视频标志位
save_video_flag = 0
# 保存图片标注位
save_image_flag = 0

#tower_Kx = 0.86

btn = 0
def draw_res(frame, results, btn):
    res = list(frame.shape)   #几行几列  转化为列表
    area = 0
    results_center = [0, 0]
    for item in results:
        #print(item)
        left = item.relative_box[0] * res[1]   #res[1]->列
        top = item.relative_box[1] * res[0]
        right = item.relative_box[2] * res[1]
        bottom = item.relative_box[3] * res[0]
        start_point = (int(left), int(top))
        end_point = (int(right), int(bottom))
        width = end_point[0] - start_point[0]
        height = end_point[1] - start_point[1]
        #print(str(width) + 'dfas' + str(height))
        if width <= 0 or height <= 0:
            width = 0
            height = 0
        results_center[0] = int(left) + width/2  #x轴中心
        results_center[1] = int(top) + height/2
        area = width * height
        #print("area:" + str(area))
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
    return frame, area, results_center


def black_img(frame):
    frame[0:120][0:640] = 0
    frame[400:480][0:640] = 0
    return frame


tower_list = [0, 0, 0, 0, 0]
target_list = [0, 0, 0, 0, 0]
lump_list = [0, 0, 0, 0, 0]
campsite_list = [0, 0, 0, 0, 0]


if __name__ == "__main__":
    ###############
    front_camera = Camera(config.front_cam, [640, 400])  # 行的长度640，列的宽度480
    side_camera = Camera(config.side_cam, [640, 480])
    front_camera.start()
    side_camera.start()
    time.sleep(3)
    rab_pwm_servo = Servo_pwm(2)  # 夹块舵机
    camera_servo = Servo(1)  # 1摄像头舵机
    dunhuang_servo = Servo_pwm(3)  # 敦煌旗帜
    daijun_servo = Servo_pwm(4)  # 代郡旗帜
    dingxiagn_servo = Servo_pwm(5)  # 定襄旗帜
    target_motor = Motor_rotate(2)
    rab_servo = Servo(2)
    sd = SignDetector()
    time.sleep(1)
    ###############
    # 巡航参数
    car_speed = 45
    angle_pid_flag = 0
    tower_Kx = 0.86
    target_Kx = 0.82
    lump_Kx = 1.0
    campsite_Kx = 0.89
    driver.set_speed(car_speed)

    rab_pwm_servo.servocontrol(60, 50)  ################
    tower_num = 0
    target_num = 0

    #driver.cart.Kx = tower_Kx
    while True:
        front_image = front_camera.read()
        front_image = black_img(front_image)
        driver.set_speed(car_speed)  # 设定self.full_speed,self.cart.velocity
        driver.cart.Kx = tower_Kx  # 转弯系数
        driver.cart.slow_ratio = 1
        res = driver.go(front_image)  # 对front图片预测并输出res(偏差)
        print(res)
        #driver.cart.steer(res)
        signs, index = sd.detect(front_image)
        sign_center = [0, 0]
        if len(signs) > 0:
            btn += 1
            frame, area, sign_center = draw_res(front_image, signs, btn)
            driver.cart.steer(res)
        else:
            driver.cart.steer(res)
        #print(res)
        #detectors-detect-infer_ssd注释了输出坐标out.shape


        #城堡识别并举旗
        if len(signs) > 0 and signs[0].name == "tower":
            del (tower_list[0])  #删除列表数据
            tower_list.append(1)   #添加到列表末尾1
            print("tower_list=", tower_list)   ##########
            if tower_list.count(1) > 1 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 180:#and abs(res) < 0.1 and area > 5500:
                time.sleep(0.42)
                driver.cart.move([0, 0, 0, 0])#检测到地标后走到某种状态后再走0.42s后到达停止
                tower_num += 1
                print("tower_num=", tower_num)
                td = TaskDetector()  # 侧边检测模型
                if tower_num == 1 or tower_num == 3:
                    camera_servo.servocontrol(124, 50)
                elif tower_num == 2:
                    camera_servo.servocontrol(-40, 50)#根据第几个城堡 转动摄像头到合适位置
                time.sleep(1)
                find_tower_frame_num = 0
                find_tower_flag = 0
                tasks = [0, 0]
                forward_flag = 0
                backward_flag = 0#初始化
                for i in range(30):
                    print("i=", i)
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    print("tasks=", tasks)#将侧边摄像头读到的任务内容检测
                    if len(tasks) > 0 and score > 0.75 and (tasks[0].name == 'daijun' or tasks[0].name == 'dunhuang' or tasks[0].name == 'dingxiang'):
                        btn += 1
                        draw_res(side_image, tasks, btn)
                        find_tower_frame_num += 1
                        print(tasks[0].name)
                    print("find_tower_frame_num=", find_tower_frame_num)
                    if find_tower_frame_num >= 3: # 5
                        find_tower_flag = 1#多次循环确认任务类型
                        if forward_flag == 1:
                            print("forward_flag向后走")
                            forward_flag = 0
                            driver.cart.move([-15, 15, -15, 15])
                            time.sleep(1.3)
                            driver.cart.move([0, 0, 0, 0])
                        if backward_flag == 1:
                            print("backward_flag向前走")
                            backward_flag = 0
                            driver.cart.move([15, -15, 15, -15])
                            time.sleep(1.3)
                            driver.cart.move([0, 0, 0, 0])
                        break
                    if i == 10 and find_tower_flag == 0:
                        print("i == 10 and find_tower_flag == 0向前")
                        find_tower_frame_num = 0
                        forward_flag = 1
                        backward_flag = 0
                        driver.cart.move([15, -15, 15, -15])
                        time.sleep(1.3)
                        driver.cart.move([0, 0, 0, 0])
                    if i == 20 and find_tower_flag == 0:
                        print("i == 20 and find_tower_flag == 0向后")
                        find_tower_frame_num = 0
                        forward_flag = 0
                        backward_flag = 1
                        driver.cart.move([-15, 15, -15, 15])
                        time.sleep(2.6)
                        driver.cart.move([0, 0, 0, 0])
                if forward_flag == 1:
                    print("forward_flag == 1向后")
                    forward_flag = 0
                    driver.cart.move([-15, 15, -15, 15])
                    time.sleep(1.3)
                    driver.cart.move([0, 0, 0, 0])
                if backward_flag == 1:
                    print("forward_flag == 1向前")
                    backward_flag = 0
                    driver.cart.move([15, -15, 15, -15])
                    time.sleep(1.3)
                    driver.cart.move([0, 0, 0, 0])#调整过程使其在地标上举旗
                print('find_tower_flag = ', find_tower_flag)
                driver.cart.Kx = tower_Kx
                angle_pid_flag = 1
                if len(tasks) > 0 and tasks[0].name == 'dunhuang':
                    print(tasks[0].name)
                    dunhuang_servo.servocontrol(85, 50)
                    time.sleep(0.1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        led.lightoff()
                    dunhuang_servo.servocontrol(-15, 50)#敦煌任务
                elif len(tasks) > 0 and tasks[0].name == "daijun":
                    print(tasks[0].name)
                    daijun_servo.servocontrol(45, 80)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        led.lightoff()
                    daijun_servo.servocontrol(-5, 50)#代郡任务
                elif len(tasks) > 0 and tasks[0].name == "dingxiang":
                    print(tasks[0].name)
                    dingxiagn_servo.servocontrol(45, 80)
                    time.sleep(0.1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        led.lightoff()
                    dingxiagn_servo.servocontrol(-1, 80)#定襄任务

        else:
            del (tower_list[0])
            tower_list.append(0)

        # 打把
        if len(signs) > 0 and signs[0].name == "target":#地标
            del (target_list[0])
            target_list.append(1)
            if target_list.count(1) > 1 and sign_center[1] > 260 and abs(sign_center[0] - 320) < 180:
                driver.cart.Kx = target_Kx
                angle_pid_flag = 0
                driver.cart.move([0, 0, 0, 0])#距离地标一段距离后停止
                td = TaskDetector()
                camera_servo.servocontrol(-40, 50)
                time.sleep(1)
                zhuan_flag = 0#
                x1_flag = 0#
                last_target_center = [0, 0]
                last_last_target_center = [0, 0]
                target_center = [0, 0]
                nfind_target_flag = 0#  #初始化
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
                        res = -0.05#控制res不要过大防止下面转弯调节位置太快
                    find_target_flag = 0#
                    target_center_x = 0#
                    if len(tasks) > 0 and score > 0.5 and tasks[0].name == 'red_target':
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        find_target_flag = 1#找到目标 可以开始调整位置准备打靶
                    elif len(tasks) == 0 and zhuan_flag == 1:
                        print("no find!")
                        driver.cart.move([-10, 10, -10, 10])#向后走
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        nfind_target_flag += 1
                    if abs(res) > 0.02 and zhuan_flag == 0:#转弯过后 调整车位置 使其接下来可以直行
                        print("res > 0.02!!!!!!!!!!!")
                        val = 30 * res
                        print(val)
                        if val < 10:
                            val = 10
                        elif val > 25:
                            val = 10
                        print(val)
                        driver.cart.move([val, val, val, val])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        continue
                    elif abs(res) < 0.02 and zhuan_flag == 0:
                        driver.cart.move([15, -15, 15, -15])#向前
                        time.sleep(1.8)
                        driver.cart.move([0, 0, 0, 0])
                           #time.sleep(1)`
                        zhuan_flag = 1#不让他重复进入循环
                    if find_target_flag == 1 and abs(target_center[1] - 200) < 15 and x1_flag == 0:# y 185~215
                        x1_flag = 1
                    elif find_target_flag == 1 and target_center[1] - 200 > 15 and x1_flag == 0:#y >215
                        driver.cart.move([-20, -20, 20, 20])#远离靶子(y近大远小
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_target_flag == 1 and target_center[1] - 200 < -15 and x1_flag == 0:#y <185
                        driver.cart.move([20, 20, -20, -20])#靠近靶子
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    if (find_target_flag == 1 and x1_flag == 1 and abs(
                                int(target_center[0]) - 295) < 1 and zhuan_flag) or i == 79 or nfind_target_flag == 5:#294<x<296 zhuan_flag=1  太久没找到放弃
                        print("iiiiiiiiiiiii=== ", i)
                        print("nfind_target_flag=", nfind_target_flag)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        target_motor.motor_rotate(-40)
                        time.sleep(0.5)
                        target_motor.motor_rotate(0)
                        time.sleep(0.5)
                        target_motor.motor_rotate(15)
                        time.sleep(3.2)
                        target_motor.motor_rotate(0)#打靶过程
                        time.sleep(1)
                        driver.cart.move([-10, -10, 10, 10])#远离靶子
                        time.sleep(0.4)
                        driver.cart.move([0, 0, 0, 0])
                        target_num += 1
                        print("target_num =", target_num)
                        driver.set_speed(car_speed)
                        break
                    elif find_target_flag == 1 and x1_flag == 1 and (
                                int(target_center[0]) - 295) > 1 and zhuan_flag:#x > 296
                        driver.cart.move([-8, 8, -8, 8])#向后
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_target_flag == 1 and x1_flag == 1 and (
                                int(target_center[0]) - 295) < -1 and zhuan_flag:#x < 294
                        driver.cart.move([8, -8, 8, -8])#向前
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
        else:
             del (target_list[0])
             target_list.append(0)
        #夹块
        if len(signs) > 0 and signs[0].name == "lump" and area > 3500 and area < 12000:
            btn += 1
            front_image, target_area, target_center = draw_res(front_image, signs, btn)
            print("area=", area)
            del (lump_list[0])
            lump_list.append(1)
            if lump_list.count(1) > 2 and area > 4500:
                btn += 1
                front_image, target_area, target_center = draw_res(front_image, signs, btn)
                driver.cart.Kx = lump_Kx
                angle_pid_flag = 0
                driver.cart.move([0, 0, 0, 0])
                td = TaskDetector()
                camera_servo.servocontrol(124, 50)
                time.sleep(1)
                x_flag = 0
                zhuan_flag = 0
                nfind_rab_num = 0  # TODO
                for i in range(100):
                    front_image = front_camera.read()
                    front_image = black_img(front_image)
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    res = driver.go(front_image)
                    find_rab_flag = 0#TODO
                    if len(tasks) > 0 and score > 0.6 and tasks[0].name == 'rab':
                        btn += 1
                        side_image, rab_area, rab_center = draw_res(side_image, tasks, btn)
                        find_rab_flag = 1
                        nfind_rab_num = 0
                        print("find,rab_center=", rab_center)
                    elif len(tasks) == 0 and zhuan_flag == 1:#abs(res) < 0.07
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([10, -10, 10, -10])#向前
                        time.sleep(0.1)
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        nfind_rab_num += 1
                    if nfind_rab_num >= 8:
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([20, 20, -20, -20])#远离kuai
                        time.sleep(0.4)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.set_speed(car_speed)
                        break


                    if abs(res) > 0.07 and zhuan_flag == 0:#调节转弯
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        val = 30 * res
                        if val < 10:
                            val = 10
                        driver.cart.move([val, val, val, val])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        continue
                    elif abs(res) < 0.07 and zhuan_flag == 0:
                        for _ in range(15):
                            btn += 1
                            side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                            driver.cart.move([15, -15, 15, -15])#向前
                            time.sleep(0.1)
                            btn += 1
                            side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([0, 0, 0, 0])
                        #time.sleep(1)
                        zhuan_flag = 1
                    if find_rab_flag == 1 and (abs(rab_center[1] - 360) < 5 and abs(
                        rab_center[0] - 320) < 15 and zhuan_flag) or i == 99:  # 找到目标 框的中心355 < y < 365  305 < x < 335 /太久没找到
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([-15, 15, -15, 15])  # 向后
                        time.sleep(0.8)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        rab_pwm_servo.servocontrol(120, 50)
                        time.sleep(0.5)
                        rab_servo.servocontrol(80, 60)
                        time.sleep(1)
                        rab_pwm_servo.servocontrol(12, 50)
                        time.sleep(0.5)
                        rab_servo.servocontrol(15, 80)
                        time.sleep(1)
                        driver.cart.move([20, 20, -20, -20])#远离
                        time.sleep(0.25)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        flag = 0
                        driver.set_speed(car_speed)
                        break
                    elif find_rab_flag == 1 and abs(rab_center[1] - 360) < 5 and rab_center[0] - 320 < -15 and zhuan_flag:#355 < y <365   x<305
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([-10, 10, -10, 10])#向后一丢丢
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    elif find_rab_flag == 1 and abs(rab_center[1] - 360) < 5 and rab_center[0] - 320 > 15 and zhuan_flag:#355 < y <365   x>335
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([10, -10, 10, -10])#向前一丢丢
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    elif find_rab_flag == 1 and rab_center[1] - 360 < -5 and abs(rab_center[0] - 320) < 15 and zhuan_flag:#y<355   305<x<335
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([-10, -10, 10, 10])#靠近一丢丢
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    elif find_rab_flag == 1 and rab_center[1] - 360 < -5 and rab_center[0] - 320 < -15 and zhuan_flag:#y<355   x<305
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([-15, 0, 0, 15])#左后一丢丢
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    elif find_rab_flag == 1 and rab_center[1] - 360 < -5 and rab_center[0] - 320 > 15 and zhuan_flag:#y<355    x>335
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([0, -15, 15, 0])#左前一丢丢
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    elif find_rab_flag == 1 and rab_center[1] - 360 > 5 and abs(rab_center[0] - 320) < 15 and zhuan_flag:#y>365   305<x<335
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([10, 10, -10, -10])#远离一丢u的
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    elif find_rab_flag == 1 and rab_center[1] - 360 > 5 and rab_center[0] - 320 < -15 and zhuan_flag:#y>365  x<305
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([0, 15, -15, 0])#右后一丢丢
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    elif find_rab_flag == 1 and rab_center[1] - 360 > 5 and rab_center[0] - 320 > 15 and zhuan_flag:#y>365  x>335
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([15, 0, 0, -15])#左前一丢丢
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
        else:
            del (lump_list[0])
            lump_list.append(0)
        #营地
        if len(signs) > 0 and signs[0].name == "campsite":
            btn += 1
            front_image, target_area, target_center = draw_res(front_image, signs, btn)
            del (campsite_list[0])
            campsite_list.append(1)
            if campsite_list.count(1) > 2 and area > 3500 and area < 24000 and abs(sign_center[1] - 320) < 50:#270< y <370
                btn += 1
                front_image, target_area, target_center = draw_res(front_image, signs, btn)
                time.sleep(0.3)#0.4
                driver.cart.move([0, 0, 0, 0])
                td = TaskDetector()
                camera_servo.servocontrol(-44, 50)
                time.sleep(1)
                for _ in range(7):#10
                    btn += 1
                    front_image, target_area, target_center = draw_res(front_image, signs, btn)
                    driver.cart.move([-50, -50, 50, 50])#靠近 走一点点
                    time.sleep(0.1)
                driver.cart.move([0, 0, 0, 0])
                for i in range(100):
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    btn += 1
                    side_image, campsite_list1, campsite_center = draw_res(side_image, tasks, btn)
                    find_campsite_flag = 0  #初始化
                    if len(tasks) > 0 and score > 0.7 and tasks[0].name == 'campsite':
                        btn += 1
                        side_image, campsite_list1, campsite_center = draw_res(side_image, tasks, btn)
                        find_campsite_flag = 1
                        print("campsite_center(y)=", campsite_center[1])
                    if (find_campsite_flag == 1 and abs(campsite_center[1] - 260) < 10) or i == 99:#250 < y < 270 / 太久了#TODO 调整值防止走过
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.Kx = campsite_Kx
                        angle_pid_flag = 0
                        driver.cart.move([0, 0, 0, 0])#入库停车
                        for i in range(3):#闪灯三次
                            print("succeed！")
                            led.lightcontrol(2, 255, 0, 0)#2号亮红灯
                            led.lightoff()
                        break
                    elif find_campsite_flag == 1 and campsite_center[1] - 260 > 10:#y > 270 还没走到位置
                        print("haven't arrive!")
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([-20, -20, 20, 20])#靠近 往里走一些  走到满足位置要求
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    elif find_campsite_flag ==1 and campsite_center[1] - 260 < -10:#y < 250 走得太靠里了
                        print("too far!")
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                        driver.cart.move([20, 20, -20, -20])#远离 往外走一点 走到满足位置要求
                        btn += 1
                        side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                for _ in range(5):#9
                    btn += 1
                    side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                    driver.cart.move([50, 50, -50, -50])#远离 往外走一丢丢
                    time.sleep(0.1)
                    btn += 1
                    side_image, target_area, target_center = draw_res(side_image, tasks, btn)
                driver.cart.move([0, 0, 0, 0])
                time.sleep(1)
        else:
            print("campsite_list=", campsite_list)
            del (campsite_list[0])
            campsite_list.append(0)



