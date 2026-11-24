import cv2
import time
from cruiser import Cruiser
from detectors import SignDetector, Trade_two, Task_Purchase, TaskDetector, Task_Person, Task_Purchase_1
# from detectors import TaskDetector_New
from camera import Camera
import config
from driver import Driver
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate, UltrasonicSensor, Buzzer, startmachine, Button, Light
from knn import knn
from tasks import *
import math


moto_stretch = Motor_rotate(1)
servo_lift = Servo(1)
servo_cam = Servo(2)
driver = Driver()
cruiser = Cruiser()

led = Light(1)
buzzer = Buzzer()
moto2 = Motor_rotate(2)
# moto3 = Motor_rotate(3)
hit_right = Motor_rotate(4)
hit_left = Servo_pwm(5)

start_button = Button(1, "4")

stop_button = Button(1, "2")
# left_button
kill_button = Button(1, "1")

cruiser_button = Button(1, "3")
# 保存视频标志位
save_video_flag = 0
pwm_hit = Servo_pwm(3)
# 保存图片标注位
save_image_flag = 0
filter_flag = 0
image_num = 10916
#pwm_clip = Servo_pwm(2)
image_dir = "/run/media/sda1/front720"

trade_up_center = [194.5, 284.5]  # [344, 244]
trade_down_center = [230, 398.5]
perchase_center_right = [235.0, 430.0]
fanwei_up = 385
fanwei_down = 328
up_or_down_flag = 0
find_trade_flag = 0


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

def draw_res_pur(frame, results, target):
    res = list(frame.shape)
    area = 0
    results_center = [0, 0]
    for item in results:
        if item.name == target:
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
        results_center[0] = int(left) + width / 2
        results_center[1] = int(top) + height / 2
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
    # frame[0:80][0:640] = 0
    frame[0:240][0:640] = 0
    return frame


tower_list = [0, 0, 0, 0, 0]
protect_list = [0, 0, 0, 0, 0]
trade_list = [0, 0, 0, 0, 0]
purchase_list = [0, 0, 0, 0, 0]
campsite_list = [0, 0, 0, 0, 0]

person_hight_record = []
person_hight_stand = [1, 2, 3, 4]
person_hight_servo = [0, -20, -50, -120, -120]

if __name__ == "__main__":
    startmachine()
    led.lightoff()

    front_camera = Camera(config.front_cam, [640, 480])
    side_camera = Camera(config.side_cam, [640, 480])

    front_camera.start()
    side_camera.start()
    time.sleep(0.5)
    sd = SignDetector()
    tt = Trade_two()
    td = TaskDetector()
    tper = Task_Person()
    tp = Task_Purchase()
    tp1 = Task_Purchase_1()
    time.sleep(0.5)

    car_speed = 46
    tower_speed_1 = 50
    tower_speed_2 = 42
    tower_speed_3 = 42
    protect_speed_1 = 35
    protect_speed_2 = 42
    protect_speed_3 = 50
    protect_speed_4 = 55
    campsite_speed = 38
    purchase_speed = 45
    trade_speed = 52

    first_Kx = 1.25

    tower_Kx_1 = 1.08
    tower_Kx_2 = 1.23
    tower_Kx_3 = 1.19
    protect_Kx_1 = 1.98
    protect_Kx_2 = 1.0
    protect_Kx_3 = 0.9
    protect_Kx_4 = 0.9

    purchase_Kx = 1.0
    campsite_Kx = 1.15
    trade_Kx = 0.9

    # angle_pid_flag = 0

    driver.set_speed(car_speed)
    driver.cart.Kx = first_Kx
    driver.cart.slow_ratio = 1

    pwm_clip = Servo_pwm(4)
    uls = UltrasonicSensor(4)
    right_button_flag = 0
    tower_num = 1
    protect_num = 1
    up_or_down = -1
    find_perchase_flag = 0
    bad_person_num = 1
    bad_or_good_list = [0, 0]
    bad_or_good_index = -1
    res_last = 0.0
    res_last_last = 0.0
    black_flag = 0
    cruiser_flag = 0
    buzzer.rings()

    while True:
        if start_button.clicked():
            # time.sleep(0.3)
            break
        #buzzer.rings()
        print("Wait for start!")


    while True:

        if kill_button.clicked():
            break

        if stop_button.clicked():
            driver.cart.move([0, 0, 0, 0])

            filter_flag = 0
            up_or_down_flag = 0
            find_trade_flag = 0

            tower_list = [0, 0, 0, 0, 0]
            protect_list = [0, 0, 0, 0, 0]
            trade_list = [0, 0, 0, 0, 0]
            purchase_list = [0, 0, 0, 0, 0]
            campsite_list = [0, 0, 0, 0, 0]

            person_hight_record = []
            person_hight_stand = [1, 2, 3, 4]
            person_hight_servo = [0, 18, -40, -70, -80]

            tower_num = 1
            protect_num = 1
            up_or_down = -1
            bad_person_num = 1
            bad_or_good_list = [0, 0]
            bad_or_good_index = -1
            res_last = 0.0
            res_last_last = 0.0
            black_flag = 0
            cruiser_flag = 0

            driver.set_speed(car_speed)
            driver.cart.Kx = first_Kx
            driver.cart.slow_ratio = 1
            print("re")

            while True:
                if start_button.clicked():
                    print("all")
                    cruiser_flag = 0
                    # time.sleep(0.3)
                    break

                if cruiser_button.clicked():
                    print("only_cruiser")
                    cruiser_flag = 1
                    break
                #buzzer.rings()
                print("Wait for start")

        front_image = front_camera.read()

        if black_flag == 1:
            front_image = black_img(front_image)

        res = driver.go(front_image)
        print(res)
        signs, index = sd.detect(front_image)
        filter_flag = 0
        sign_center = [0, 0]
        if filter_flag == 0:
            pass
        else:
            res_filter = 0.5 * res + 0.4 * res_last + 0.1 * res_last_last
            res_last_last = res_last
            res_last = res
            res = res_filter

        if len(signs) > 0:
            frame, area, sign_center = draw_res(front_image, signs)
            driver.cart.steer(res)
        else:
            driver.cart.steer(res)

        if cruiser_flag == 0:

            if len(signs) > 0 and signs[0].name == "tower":
                del (tower_list[0])
                tower_list.append(1)
                if tower_list.count(1) > 1 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 180:

                    zhuan_flag = 0

                    if tower_num == 1:
                        time.sleep(0.55)#0.8
                        driver.cart.Kx = tower_Kx_1
                        driver.set_speed(tower_speed_1)
                        driver.cart.slow_ratio = 1
                    elif tower_num == 2:
                        # time.sleep(0.65)
                        driver.cart.move([15, -15, 15, -15])
                        time.sleep(2.3)
                        driver.cart.Kx = tower_Kx_2
                        driver.set_speed(tower_speed_2)
                        driver.cart.slow_ratio = 1
                    elif tower_num == 3:
                        time.sleep(0.6)
                        # driver.cart.Kx = tower_Kx_3
                        # driver.set_speed(tower_speed_3)
                        # driver.cart.slow_ratio = 1
                        # driver.cruiser.predictor.load(config.cruise["model"])
                    driver.cart.move([0, 0, 0, 0])
                    time.sleep(0.3)

                    servo_cam.servocontrol(-41, 70)
                    time.sleep(1)
                    find_tower_frame_num = 0
                    find_tower_flag = 0
                    tasks = [0, 0]
                    forward_flag = 0
                    backward_flag = 0
                    if tower_num == 3:
                        driver.cart.Kx = tower_Kx_3
                        driver.set_speed(tower_speed_3)
                        driver.cart.slow_ratio = 1
                        # driver.cruiser.predictor.load(config.cruise["model"])


                        # for i in range(20):
                        #     if abs(res) > 0.07 and zhuan_flag == 0:
                        #         val = 30 * res
                        #         if val < 10 and val > 0:
                        #             val = 10
                        #         if val > -10 and val <= 0:
                        #             val = -10
                        #         driver.cart.move([val, val, val, val])
                        #         time.sleep(0.1)
                        #         driver.cart.move([0, 0, 0, 0])
                        #         continue
                        #     elif abs(res) < 0.07 and zhuan_flag == 0:
                        #         driver.cart.move([0, 0, 0, 0])
                        #         break
                    # if tower_num == 1:
                    #     driver.cart.Kx = tower_Kx_1
                    #     driver.set_speed(tower_speed_1)
                    #     driver.cart.slow_ratio = 1
                    #     # servo_cam.servocontrol(-47, 40)
                    #     # time.sleep(1)
                    # if tower_num == 2:
                    #     driver.cart.Kx = tower_Kx_2
                    #     driver.set_speed(tower_speed_2)
                    #     driver.cart.slow_ratio = 1
                    #     # servo_cam.servocontrol(-47, 40)
                    #     # time.sleep(1)
                    # if tower_num == 3:
                    #     driver.cart.Kx = tower_Kx_3
                    #     driver.set_speed(tower_speed_3)
                    #     driver.cart.slow_ratio = 1
                    #     driver.cruiser.predictor.load(config.cruise["model"])

                    if tower_num == 2:
                        for i in range(20):
                            front_image = front_camera.read()
                            res = driver.go(front_image)
                            if abs(res) > 0.1:
                                val = 30 * res
                                if val < 10 and val > 0:
                                    val = 10
                                if val > -10 and val <= 0:
                                    val = -10
                                driver.cart.move([val, val, val, val])
                                time.sleep(0.1)
                                driver.cart.move([0, 0, 0, 0])
                                continue
                            elif abs(res) < 0.1:
                                driver.cart.move([0, 0, 0, 0])
                                break

                    for i in range(30):
                        side_image = side_camera.read()
                        tasks, score = td.detect(side_image)
                        if len(tasks) > 0 and score > 0.5 and (tasks[0].name == 'alamutu' or tasks[0].name == 'dunhuang' or tasks[0].name == 'jstdb'):

                            find_tower_frame_num += 1

                        if find_tower_frame_num >= 3:  # 5
                            # print('back_flag', backward_flag)
                            # print('forward_flag', forward_flag)
                            find_tower_flag = 1
                            if forward_flag == 1:
                                forward_flag = 0
                                driver.cart.move([-15, 15, -15, 15])
                                time.sleep(1.3)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.3)
                            if backward_flag == 1:
                                backward_flag = 0
                                driver.cart.move([15, -15, 15, -15])
                                time.sleep(1.3)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.3)
                            break
                        if i == 10 and find_tower_flag == 0:
                            find_tower_frame_num = 0
                            forward_flag = 1
                            backward_flag = 0
                            driver.cart.move([15, -15, 15, -15])
                            time.sleep(1.3)
                            driver.cart.move([0, 0, 0, 0])
                            time.sleep(0.3)
                        if i == 20 and find_tower_flag == 0:
                            find_tower_frame_num = 0
                            forward_flag = 0
                            backward_flag = 1
                            driver.cart.move([-15, 15, -15, 15])
                            time.sleep(2.6)
                            driver.cart.move([0, 0, 0, 0])
                            time.sleep(0.3)
                    if forward_flag == 1:
                        forward_flag = 0
                        driver.cart.move([-15, 15, -15, 15])
                        time.sleep(1.3)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(0.3)
                    if backward_flag == 1:
                        backward_flag = 0
                        driver.cart.move([15, -15, 15, -15])
                        time.sleep(1.3)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(0.3)

                    if len(tasks) > 0 and tasks[0].name == 'dunhuang':
                        print(tasks[0].name)
                        moto2.motor_rotate(-30)
                        time.sleep(0.17)  # 初到左
                        moto2.motor_rotate(0)
                        time.sleep(1)
                        for i in range(3):
                            led.lightcontrol(0, 0, 255, 0)
                            time.sleep(0.5)
                            led.lightoff()
                            time.sleep(0.5)
                        moto2.motor_rotate(30)
                        time.sleep(0.15)
                        moto2.motor_rotate(0)
                    elif len(tasks) > 0 and tasks[0].name == "alamutu":
                        print(tasks[0].name)
                        moto2.motor_rotate(30)
                        time.sleep(0.16)  # 初到右
                        moto2.motor_rotate(0)
                        time.sleep(0.5)
                        for i in range(3):
                            led.lightcontrol(0, 0, 255, 0)
                            time.sleep(0.5)
                            led.lightoff()
                            time.sleep(1)
                        moto2.motor_rotate(-30)
                        time.sleep(0.14)
                        moto2.motor_rotate(0)
                    elif len(tasks) > 0 and tasks[0].name == "jstdb":
                        print(tasks[0].name)
                        # time.sleep(3)
                        moto2.motor_rotate(30)
                        time.sleep(0.3)  # 初到中
                        moto2.motor_rotate(0)
                        time.sleep(1)
                        for i in range(3):
                            led.lightcontrol(0, 0, 255, 0)
                            time.sleep(0.5)
                            led.lightoff()
                            time.sleep(0.5)
                        moto2.motor_rotate(-30)
                        time.sleep(0.285)
                        moto2.motor_rotate(0)
                    tower_num = tower_num + 1

            else:
                del (tower_list[0])
                tower_list.append(0)

            if len(signs) > 0 and signs[0].name == "protect":
                del (protect_list[0])
                protect_list.append(1)
                if protect_list.count(1) > 2 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 180 and area > 7000:

                    if protect_num == 1:
                        time.sleep(0.43)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(0.1)
                        driver.cart.Kx = protect_Kx_1
                        driver.set_speed(protect_speed_1)
                        driver.cart.slow_ratio = 0.9
                        black_flag = 1
                        driver.cruiser.predictor.load(config.cruise3["model"])

                        servo_lift.servocontrol(-120, 15)
                        time.sleep(1.5)

                        zhuan_flag = 0
                        valid_num = 0
                        move_flag = 0
                        find_one_in_four_flag = 0
                        high_what = 0
                        person_list_high = [0, 0, 0, 0, 0]
                        det_flag = 0
                        bad_or_good_index = "0"
                        forward_flag = 0
                        backward_flag = 0

                        for i in range(100):
                            if zhuan_flag == 0:
                                front_image = front_camera.read()
                                res = driver.go(front_image)
                                if abs(res) > 0.07 and zhuan_flag == 0:
                                    val = 30 * res
                                    if val < 10 and val > 0:
                                        val = 10
                                    if val > -10 and val <= 0:
                                        val = -10
                                    driver.cart.move([val, val, val, val])
                                    time.sleep(0.1)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                elif abs(res) < 0.07 and zhuan_flag == 0:
                                    driver.cart.move([0, 0, 0, 0])
                                    zhuan_flag = 1


                            if det_flag == 0 and zhuan_flag == 1:
                                bad_or_good_index = identify_bad(side_camera)
                                if bad_or_good_index == "bad" or bad_or_good_index == "good":
                                    det_flag = 1
                                elif forward_flag == 0 and backward_flag == 0:
                                    driver.cart.move([15, -15, 15, -15])
                                    time.sleep(1)
                                    driver.cart.move([0, 0, 0, 0])
                                    time.sleep(0.2)
                                    forward_flag = 1
                                    continue
                                elif forward_flag == 1 and backward_flag == 0:
                                    driver.cart.move([-15, 15, -15, 15])
                                    time.sleep(2)
                                    driver.cart.move([0, 0, 0, 0])
                                    time.sleep(0.2)
                                    backward_flag = 1
                                    continue
                                elif forward_flag == 1 and backward_flag == 1:
                                    person_hight_record.append(4)
                                    print("not find anything")
                                    break

                            side_image = side_camera.read()
                            result, score = tper.detect(side_image)
                            frame, area, sign_center = draw_res(side_image, result)
                            print(area, sign_center)


                            if zhuan_flag == 1 and move_flag == 0 and sign_center[0] > 0 and det_flag == 1:
                                if sign_center[0] - 333 < -75:
                                    driver.cart.move([-15, 15, -15, 15])
                                    time.sleep(0.45)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                if -75 < sign_center[0] - 333 < -10:
                                    driver.cart.move([-10, 10, -10, 10])
                                    time.sleep(0.07)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                if 10 < sign_center[0] - 333 < 75:
                                    driver.cart.move([10, -10, 10, -10])
                                    time.sleep(0.07)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                if sign_center[0] - 333 > 75:
                                    driver.cart.move([15, -15, 15, -15])
                                    time.sleep(0.45)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                if abs(sign_center[0] - 333) < 10:
                                    valid_num = valid_num + 1
                                print("valid", valid_num)
                            if zhuan_flag == 1 and valid_num > 5 and move_flag == 0:
                                driver.cart.move([-20, 20, -20, 20])
                                time.sleep(0.45)
                                driver.cart.move([0, 0, 0, 0])
                                move_flag = 1
                            if zhuan_flag == 1 and move_flag == 1 and find_one_in_four_flag == 0:
                                for i in range(8):
                                    side_image = side_camera.read()
                                    result, score = tper.detect(side_image)
                                    distance = uls.read()
                                    frame, area, sign_center = draw_res(side_image, result)
                                    print(distance, area, sign_center)
                                    if type(distance) == int and distance < 63 and len(result) > 0:

                                        this = knn(distance, area, sign_center[1])
                                        person_list_high[this] = person_list_high[this] + 1
                                    print("person_list_high", person_list_high)
                                high_what = person_list_high.index(max(person_list_high))
                                person_hight_record.append(high_what)
                                find_one_in_four_flag = 1
                                if bad_or_good_index == "good":
                                    break

                            if bad_or_good_index == "bad" and high_what == 1:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == "bad" and high_what == 2:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == "bad" and high_what == 3:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == "bad" and (high_what == 4 or i == 99):
                                high_what = 4
                                hit_person(high_what)
                                bad_person_num += 1
                                break

                    if protect_num == 2:
                        time.sleep(0.43)#0.53
                        driver.cart.Kx = protect_Kx_2
                        driver.set_speed(protect_speed_2)
                        driver.cart.slow_ratio = 1

                        # driver.cruiser.predictor.load(config.cruise["model"])
                        # if bad_person_num <= 2:
                        # driver.cart.move([10,-10,10,-10])
                        # time.sleep(0.9)

                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(0.2)
                        # servo_cam.servocontrol(-47, 40)
                        # time.sleep(1.0)
                        servo_lift.servocontrol(-120, 10)
                        time.sleep(0.5)
                        bad_or_good_list = [0, 0]
                        zhuan_flag = 0
                        # driver.cruiser.predictor.load(config.cruise["model"])
                        black_flag = 0
                        valid_num = 0
                        move_flag = 0

                        find_one_in_four_flag = 0
                        high_what = 0
                        person_list_high = [0, 0, 0, 0, 0]
                        det_flag = 0
                        bad_or_good_index = "0"
                        forward_flag = 0
                        backward_flag = 0
                        # mode_flag = 0

                        for i in range(100):
                            if zhuan_flag == 0:
                                front_image = front_camera.read()
                                res = driver.go(front_image)
                                if abs(res + 0.29) > 0.02:
                                    val = 30 * (res + 0.29)
                                    if val < 10 and val > 0:
                                        val = 10
                                    if val > -10 and val <= 0:
                                        val = -10
                                    driver.cart.move([val, val, val, val])
                                    time.sleep(0.1)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                elif abs(res + 0.29) < 0.02:
                                    driver.cart.move([0, 0, 0, 0])
                                    zhuan_flag = 1
                                    driver.cruiser.predictor.load(config.cruise["model"])
                                    # time.sleep(1)


                            if det_flag == 0 and zhuan_flag == 1:
                                bad_or_good_index = identify_bad(side_camera)
                                if bad_or_good_index == "bad" or bad_or_good_index == "good":
                                    det_flag = 1
                                elif forward_flag == 0 and backward_flag == 0:
                                    driver.cart.move([15, -15, 15, -15])
                                    time.sleep(1)
                                    driver.cart.move([0, 0, 0, 0])
                                    time.sleep(0.2)
                                    forward_flag = 1
                                    continue
                                elif forward_flag == 1 and backward_flag == 0:
                                    driver.cart.move([-15, 15, -15, 15])
                                    time.sleep(2)
                                    driver.cart.move([0, 0, 0, 0])
                                    time.sleep(0.2)
                                    backward_flag = 1
                                    continue
                                elif forward_flag == 1 and backward_flag == 1:
                                    person_hight_record.append(3)
                                    print("not find anything")
                                    break

                            side_image = side_camera.read()
                            result, score = tper.detect(side_image)
                            frame, area, sign_center = draw_res(side_image, result)

                            if zhuan_flag == 1 and move_flag == 0 and sign_center[0] > 0 and det_flag == 1:
                                if sign_center[0] - 333 < -75:
                                    driver.cart.move([-15, 15, -15, 15])
                                    time.sleep(0.45)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                if -75 < sign_center[0] - 333 < -10:
                                    driver.cart.move([-10, 10, -10, 10])
                                    time.sleep(0.07)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                if 10 < sign_center[0] - 333 < 75:
                                    driver.cart.move([10, -10, 10, -10])
                                    time.sleep(0.07)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                if sign_center[0] - 333 > 75:
                                    driver.cart.move([15, -15, 15, -15])
                                    time.sleep(0.45)
                                    driver.cart.move([0, 0, 0, 0])
                                    continue
                                if abs(sign_center[0] - 333) < 10:
                                    valid_num = valid_num + 1
                                print("valid_number", valid_num)

                            if zhuan_flag == 1 and valid_num > 4 and move_flag == 0:
                                driver.cart.move([-20, 20, -20, 20])
                                time.sleep(0.45)
                                driver.cart.move([0, 0, 0, 0])
                                move_flag = 1

                            print("move_flag", move_flag)
                            if zhuan_flag == 1 and move_flag == 1 and find_one_in_four_flag == 0:
                                for i in range(8):
                                    side_image = side_camera.read()
                                    result, score = tper.detect(side_image)
                                    distance = uls.read()
                                    frame, area, sign_center = draw_res(side_image, result)
                                    print(distance, area, sign_center)
                                    if type(distance) == int and distance < 63 and len(result) > 0:
                                        # if score > 0.5 and (result[0].name == 'badperson' or result[0].name == 'badperson2'):
                                        this = knn(distance, area, sign_center[1])
                                        person_list_high[this] = person_list_high[this] + 1
                                    print("person_list_high", person_list_high)
                                high_what = person_list_high.index(max(person_list_high))
                                print("high_what", high_what)
                                person_hight_record.append(high_what)
                                find_one_in_four_flag = 1
                                if bad_or_good_index == "good":
                                    break

                            if bad_or_good_index == "bad" and high_what == 1:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == "bad" and high_what == 2:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == "bad" and (high_what == 3 or i == 99):
                                high_what = 3
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == "bad" and high_what == 4:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                    if protect_num == 3:
                        time.sleep(0.68)
                        driver.cart.Kx = protect_Kx_1
                        driver.set_speed(protect_speed_1)
                        driver.cart.slow_ratio = 1
                        # driver.cruiser.predictor.load(config.cruise2["model"])
                        if bad_person_num <= 2:
                            driver.cart.move([0, 0, 0, 0])
                            time.sleep(0.5)
                            # servo_cam.servocontrol(-47, 40)
                            # time.sleep(1.0)
                            servo_lift.servocontrol(-120, 30)
                            time.sleep(0.7)
                            zhuan_flag = 0
                            det_flag = 0
                            bad_or_good_index = "0"
                            forward_flag = 0
                            backward_flag = 0

                            move_flag = 0
                            valid_num = 0
                            find_one_in_four_flag = 0
                            high_what = 0
                            person_list_high = [0, 0, 0, 0, 0]
                            for i in range(100):
                                if zhuan_flag == 0:
                                    front_image = front_camera.read()
                                    res = driver.go(front_image)
                                    if abs(res) > 0.07 and zhuan_flag == 0:
                                        val = 30 * res
                                        if val < 10 and val > 0:
                                            val = 10
                                        if val > -10 and val <= 0:
                                            val = -10
                                        driver.cart.move([val, val, val, val])
                                        time.sleep(0.1)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    elif abs(res) < 0.07 and zhuan_flag == 0:
                                        driver.cart.move([0, 0, 0, 0])
                                        # time.sleep(1)
                                        zhuan_flag = 1

                                if det_flag == 0 and zhuan_flag == 1:
                                    bad_or_good_index = identify_bad(side_camera)
                                    if bad_or_good_index == "bad" or bad_or_good_index == "good":
                                        det_flag = 1
                                    elif forward_flag == 0 and backward_flag == 0:
                                        driver.cart.move([15, -15, 15, -15])
                                        time.sleep(1)
                                        driver.cart.move([0, 0, 0, 0])
                                        time.sleep(0.2)
                                        forward_flag = 1
                                        continue
                                    elif forward_flag == 1 and backward_flag == 0:
                                        driver.cart.move([-15, 15, -15, 15])
                                        time.sleep(2)
                                        driver.cart.move([0, 0, 0, 0])
                                        time.sleep(0.2)
                                        backward_flag = 1
                                        continue
                                    elif forward_flag == 1 and backward_flag == 1:
                                        person_hight_record.append(1)
                                        print("not find anything")
                                        break

                                side_image = side_camera.read()
                                result, score = tper.detect(side_image)
                                frame, area, sign_center = draw_res(side_image, result)

                                if zhuan_flag == 1 and move_flag == 0 and sign_center[0] > 0:
                                    if sign_center[0] - 333 < -75:
                                        driver.cart.move([-15, 15, -15, 15])
                                        time.sleep(0.45)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    if -75 < sign_center[0] - 333 < -10:
                                        driver.cart.move([-10, 10, -10, 10])
                                        time.sleep(0.07)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    if 10 < sign_center[0] - 333 < 75:
                                        driver.cart.move([10, -10, 10, -10])
                                        time.sleep(0.07)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    if sign_center[0] - 333 > 75:
                                        driver.cart.move([15, -15, 15, -15])
                                        time.sleep(0.45)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    if abs(sign_center[0] - 333) < 10:
                                        valid_num = valid_num + 1
                                if zhuan_flag == 1 and valid_num > 5 and move_flag == 0:
                                    driver.cart.move([-20, 20, -20, 20])
                                    time.sleep(0.45)
                                    driver.cart.move([0, 0, 0, 0])
                                    move_flag = 1
                                if zhuan_flag == 1 and move_flag == 1 and find_one_in_four_flag == 0:
                                    for i in range(8):
                                        side_image = side_camera.read()
                                        result, score = tper.detect(side_image)
                                        distance = uls.read()
                                        frame, area, sign_center = draw_res(side_image, result)
                                        print(distance, area, sign_center)
                                        if type(distance) == int and distance < 63 and len(result) > 0:
                                            # if score > 0.5 and (result[0].name == 'badperson' or result[0].name == 'badperson2'):
                                            this = knn(distance, area, sign_center[1])
                                            person_list_high[this] = person_list_high[this] + 1
                                            print("person_list_high", person_list_high)
                                    high_what = person_list_high.index(max(person_list_high))
                                    person_hight_record.append(high_what)
                                    find_one_in_four_flag = 1
                                    if bad_or_good_index == "good":
                                        break

                                if bad_or_good_index == "bad" and (high_what == 1 or i == 99):
                                    high_what = 1
                                    hit_person(high_what)
                                    bad_person_num += 1
                                    break
                                elif bad_or_good_index == "bad" and high_what == 2:
                                    hit_person(high_what)
                                    bad_person_num += 1
                                    break
                                elif bad_or_good_index == "bad" and high_what == 3:
                                    hit_person(high_what)
                                    bad_person_num += 1
                                    break
                                elif bad_or_good_index == "bad" and high_what == 4:
                                    hit_person(high_what)
                                    bad_person_num += 1
                                    break
                    if protect_num == 4:
                        # time.sleep(0.93)
                        driver.cart.Kx = protect_Kx_4
                        driver.set_speed(protect_speed_4)
                        driver.cart.slow_ratio = 1
                        # driver.cruiser.predictor.load(config.cruise["model"])
                        if bad_person_num <= 2:
                            time.sleep(0.37)
                            driver.cart.move([0, 0, 0, 0])
                            time.sleep(0.5)
                            servo_cam.servocontrol(120, 70)
                            time.sleep(1)
                            protect_4_hight_index = [high_index for high_index in person_hight_stand if
                                                     high_index not in person_hight_record]
                            protect_4_hight = person_hight_servo[protect_4_hight_index[0]]
                            zhuan_flag = 0
                            det_flag = 0
                            bad_or_good_index = "0"
                            forward_flag = 0
                            backward_flag = 0
                            valid_num = 0
                            for i in range(100):
                                if zhuan_flag == 0:
                                    front_image = front_camera.read()
                                    res = driver.go(front_image)

                                    if abs(res) > 0.07 and zhuan_flag == 0:
                                        val = 30 * res
                                        if val < 10 and val > 0:
                                            val = 10
                                        if val > -10 and val <= 0:
                                            val = -10
                                        driver.cart.move([val, val, val, val])
                                        time.sleep(0.1)
                                        driver.cart.move([0, 0, 0, 0])

                                        continue
                                    elif abs(res) < 0.07 and zhuan_flag == 0:
                                        driver.cart.move([0, 0, 0, 0])
                                        # time.sleep(1)
                                        zhuan_flag = 1

                                if det_flag == 0 and zhuan_flag == 1:
                                    bad_or_good_index = identify_bad(side_camera)
                                    if bad_or_good_index == "bad" or bad_or_good_index == "good":
                                        det_flag = 1
                                    elif forward_flag == 0 and backward_flag == 0:
                                        driver.cart.move([15, -15, 15, -15])
                                        time.sleep(1)
                                        driver.cart.move([0, 0, 0, 0])
                                        time.sleep(0.2)
                                        forward_flag = 1
                                        continue
                                    elif forward_flag == 1 and backward_flag == 0:
                                        driver.cart.move([-15, 15, -15, 15])
                                        time.sleep(2)
                                        driver.cart.move([0, 0, 0, 0])
                                        time.sleep(0.2)
                                        backward_flag = 1
                                        continue
                                    elif forward_flag == 1 and backward_flag == 1:
                                        person_hight_record.append(3)
                                        print("not find anything")
                                        break

                                if det_flag == 1 and bad_or_good_index == "good":
                                    break


                                side_image = side_camera.read()
                                result, score = tper.detect(side_image)
                                frame, area, sign_center = draw_res(side_image, result)

                                if len(result) > 0 and zhuan_flag == 1 and (
                                    result[0].name == 'badperson' or result[0].name == 'badperson2') and sign_center[0] > 0 and det_flag == 1 and bad_or_good_index == "bad":
                                    if sign_center[0] - 335 < -75:
                                        driver.cart.move([15, -15, 15, -15])
                                        time.sleep(0.45)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    if -75 < sign_center[0] - 335 < -7:
                                        driver.cart.move([10, -10, 10, -10])
                                        time.sleep(0.07)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    if 7 < sign_center[0] - 335 < 75:
                                        driver.cart.move([-10, 10, -10, 10])
                                        time.sleep(0.07)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    if sign_center[0] - 335 > 75:
                                        driver.cart.move([-15, 15, -15, 15])
                                        time.sleep(0.45)
                                        driver.cart.move([0, 0, 0, 0])
                                        continue
                                    if abs(sign_center[0] - 335) <= 7:
                                        valid_num = valid_num + 1
                                if zhuan_flag == 1 and valid_num > 5:
                                    driver.cart.move([-20, 20, -20, 20])
                                    time.sleep(1)
                                    driver.cart.move([0, 0, 0, 0])
                                    time.sleep(0.5)
                                    servo_lift.servocontrol(protect_4_hight, 75)
                                    time.sleep(1.8)
                                    hit_right.motor_rotate(-60)
                                    time.sleep(1.8)
                                    hit_right.motor_rotate(0)
                                    time.sleep(1)
                                    hit_right.motor_rotate(60)
                                    time.sleep(1.8)
                                    hit_right.motor_rotate(0)
                                    time.sleep(0.5)
                                    # moto3.motor_rotate(-55)
                                    # time.sleep(1.75)
                                    # moto3.motor_rotate(0)
                                    # time.sleep(1)
                                    # moto3.motor_rotate(55)
                                    # time.sleep(0.99)
                                    # moto3.motor_rotate(0)
                                    # time.sleep(0.5)
                                    servo_lift.servocontrol(-120, 30)  # -120
                                    time.sleep(1.5)
                                    break

                    protect_num += 1

            else:
                del (protect_list[0])
                protect_list.append(0)

            if len(signs) > 0 and signs[0].name == "purchase" and area < 12000:
                del (purchase_list[0])
                purchase_list.append(1)
                if purchase_list.count(1) > 1 and area > 5500:  # 4500
                    #time.sleep(0.01)
                    time.sleep(0.56)#0.7
                    driver.cart.move([0, 0, 0, 0])
                    #time.sleep(20000)
                    driver.cart.Kx = purchase_Kx
                    driver.set_speed(purchase_speed)
                    servo_cam.servocontrol(120, 70)
                    # tp = Task_Purchase()
                    # tp1 = Task_Purchase_1()
                    time.sleep(0.3)
                    zhuan_flag = 0
                    find_right_flag = 0
                    # time.sleep(1)
                    # find_right_flag_once = 0
                    perchase_right_list = [0, 0, 0, 0, 0, 0]
                    dong_flag = 0
                    old_tasks = 0
                    right_flag = 0
                    for i in range(101):
                        find_right_flag_once = 0
                        side_image = side_camera.read()
                        if old_tasks == 0:
                            tasks, score = tp.detect(side_image)
                        if old_tasks == 1:
                            tasks_1, score_1 = tp1.detect(side_image)
                        print(tasks, score)
                        if zhuan_flag == 0:
                            front_image = front_camera.read()
                            res = driver.go(front_image)
                            if abs(res + 0.26) > 0.07 and zhuan_flag == 0:
                                val = 30 * (res + 0.26)
                                if val < 10 and val > 0:
                                    val = 10
                                if val > -10 and val <= 0:
                                    val = -10
                                driver.cart.move([val, val, val, val])
                                time.sleep(0.1)
                                driver.cart.move([0, 0, 0, 0])
                                continue
                            elif abs(res + 0.26) < 0.07 and zhuan_flag == 0:
                                driver.cart.move([0, 0, 0, 0])
                                # time.sleep(1)
                                zhuan_flag = 1

                        if len(tasks) > 0 and find_right_flag == 0:
                            if tasks[0].name == 'blue' and score > 0.4:
                                perchase_right_list[1] = perchase_right_list[1] + 1
                            elif tasks[0].name == 'green' and score > 0.4:
                                perchase_right_list[2] = perchase_right_list[2] + 1
                            elif tasks[0].name == 'orange' and score > 0.4:
                                perchase_right_list[3] = perchase_right_list[3] + 1
                            elif tasks[0].name == 'red' and score > 0.4:
                                perchase_right_list[4] = perchase_right_list[4] + 1
                            elif tasks[0].name == 'yellow' and score > 0.4:
                                perchase_right_list[5] = perchase_right_list[5] + 1

                        if find_right_flag == 0 and max(perchase_right_list) > 5:
                            right_target_name = config.purchase_list[perchase_right_list.index(max(perchase_right_list))]
                            find_right_flag = 1
                            print("right_target_name", right_target_name)
                        if old_tasks == 0:
                            if find_right_flag == 1 and len(tasks) > 0 and tasks[0].score > 0.4 and tasks[
                                0].name == right_target_name:
                                side_image, perchase_area, perchase_center = draw_res(side_image, tasks)
                                # old_center = perchase_center
                                find_right_flag_once = 1
                                old_tasks = 1

                            # elif find_right_flag != 1 or len(tasks) > 0 or tasks[0].score < 0.4 or tasks[
                            #     0].name != right_target_name:
                            #     old_tasks = 1
                        elif old_tasks == 1:
                            if find_right_flag == 1 and len(tasks_1) > 0 and tasks_1[0].score > 0.5:
                                frame, area, perchase_center = draw_res_pur(side_image, tasks_1, right_target_name)
                                if area != 0:
                                    find_right_flag_once = 1
                                    print("center", perchase_center)
                                # old_tasks = 1

                        if find_right_flag_once == 1:
                            if dong_flag == 0:
                                front = (6.40 * 0.0000001 * perchase_center[0] * perchase_center[0] - 4.99 * 0.001 *
                                      perchase_center[0] + 1.1196) \
                                    if (6.40 * 0.0000001 * perchase_center[0] * perchase_center[0] - 4.99 * 0.001 *
                                        perchase_center[0] + 1.1196) > 0 else 0
                                behind = (-2.21 * 0.000001 * perchase_center[0] * perchase_center[0] + 0.00609 * perchase_center[
                                    0] - 1.302) \
                                    if (-2.21 * 0.000001 * perchase_center[0] * perchase_center[0] + 0.00609 * perchase_center[
                                    0] - 1.302) > 0 else 0
                                ping = (-4.3636 * 0.000001 * perchase_center[1] * perchase_center[1] - 3.5901 * 0.001 * perchase_center[
                                    1] + 2.3615) \
                                    if (-4.3636 * 0.000001 * perchase_center[1] * perchase_center[1] - 3.5901 * 0.001 * perchase_center[
                                    1] + 2.3615) > 0 else 0
                                print(front)
                                print(behind)
                                if dong_flag == 0 and 0 < perchase_center[0] < 226:
                                    driver.cart.move([15, -15, 15, -15])
                                    time.sleep(front)
                                    driver.cart.move([0, 0, 0, 0])
                                    time.sleep(0.1)
                                    if perchase_center[1] < 430:
                                        driver.cart.move([15, 15, -15, -15])
                                        time.sleep(ping)
                                    driver.cart.move([0, 0, 0, 0])
                                    dong_flag = 1
                                elif dong_flag == 0 and perchase_center[0] > 247:
                                    driver.cart.move([-15, 15, -15, 15])
                                    time.sleep(behind)
                                    driver.cart.move([0, 0, 0, 0])
                                    time.sleep(0.1)
                                    if perchase_center[1] < 430:
                                        driver.cart.move([15, 15, -15, -15])
                                        time.sleep(ping)
                                    driver.cart.move([0, 0, 0, 0])
                                    dong_flag = 1
                                elif 226 < perchase_center[0] < 247:
                                    dong_flag = 1

                            # if tasks[0].name == right_target_name:
                            if (abs(perchase_center[1] - perchase_center_right[1]) < 5 and abs(
                                    perchase_center[0] - perchase_center_right[0]) < 5) or i == 100:
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(1)
                                servo_lift.servocontrol(-75, 70)  # -60
                                time.sleep(1)
                                pwm_clip.servocontrol(52, 30)
                                time.sleep(1)
                                moto_stretch.motor_rotate(-20)
                                time.sleep(1.)#1.2
                                moto_stretch.motor_rotate(0)
                                time.sleep(1)
                                pwm_clip.servocontrol(125, 50)
                                time.sleep(1.5)
                                servo_lift.servocontrol(-50, 70)  # -45
                                time.sleep(0.9)
                                moto_stretch.motor_rotate(20)
                                time.sleep(1.)
                                moto_stretch.motor_rotate(0)
                                time.sleep(1.8)
                                driver.cart.move([-15, -15, 15, 15])
                                time.sleep(0.3)
                                break
                            elif abs(perchase_center[1] - perchase_center_right[1]) < 5 and perchase_center[0] - \
                                    perchase_center_right[0] > 5:
                                driver.cart.move([-15, 15, -15, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif abs(perchase_center[1] - perchase_center_right[1]) < 5 and perchase_center[0] - \
                                    perchase_center_right[0] < -5:
                                driver.cart.move([15, -15, 15, -15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif perchase_center[1] - perchase_center_right[1] > 5 and abs(
                                    perchase_center[0] - perchase_center_right[0]) < 5:
                                driver.cart.move([-15, -15, 15, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif perchase_center[1] - perchase_center_right[1] > 5 and perchase_center[0] - \
                                    perchase_center_right[0] > 5:
                                driver.cart.move([-15, 0, 0, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif perchase_center[1] - perchase_center_right[1] > 5 and perchase_center[0] - \
                                    perchase_center_right[0] < -5:
                                driver.cart.move([0, -15, 15, 0])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif perchase_center[1] - perchase_center_right[1] < -5 and abs(
                                    perchase_center[0] - perchase_center_right[0]) < 5:
                                driver.cart.move([15, 15, -15, -15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif perchase_center[1] - perchase_center_right[1] < -5 and perchase_center[0] - \
                                    perchase_center_right[0] > 5:
                                driver.cart.move([0, 15, -15, 0])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif perchase_center[1] - perchase_center_right[1] < -5 and perchase_center[0] - \
                                    perchase_center_right[0] < -5:
                                driver.cart.move([15, 0, 0, -15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
            else:
                del (purchase_list[0])
                purchase_list.append(0)

            if len(signs) > 0 and signs[0].name == "trade" and area > 3500 and area < 12000:
                del (trade_list[0])
                trade_list.append(1)

                if trade_list.count(1) > 1 and area > 6000:
                    # driver.cart.move([15, -15, 15, -15])
                    # for i in range(100):
                    #     side_image = side_camera.read()
                    #     tasks, score = tt.detect(side_image)
                    #     if len(tasks) > 0 and tasks[0].score > 0.4 and (
                    #             tasks[0].name == str('putao') or tasks[0].name == str('hetao')):
                    #         side_image, trade_area, trade_center = draw_res(side_image, tasks)
                    #         find_trade_flag = 1
                    #         print(trade_center)
                    #         if 310<trade_center[0] < 330:
                    #             driver.cart.move([0, 0, 0, 0])
                    #             time.sleep(10)
                    time.sleep(0.86)
                    driver.cart.move([0, 0, 0, 0])

                    driver.cart.Kx = trade_Kx
                    #tt = Trade_two()
                    driver.set_speed(trade_speed)
                    # driver.cruiser.predictor.load(config.cruise["model"])
                    # 摄像头舵机
                    time.sleep(0.7)
                    servo_cam.servocontrol(120, 70)
                    time.sleep(1.5)
                    # print("2333333333333333333333333333333333333")
                    # time.sleep(1)
                    zhuan_flag = 0
                    not_find_flag = 0
                    hou_flag = 0
                    qian_flag = 3
                    trade_height_list = [0, 0]
                    up_or_down_list = [0, 0]
                    front_image = front_camera.read()
                    res = driver.go(front_image)
                    trade_center = [0, 0]

                    for i in range(101):
                        side_image = side_camera.read()
                        tasks, score = tt.detect(side_image)
                        print(tasks, score)

                        if zhuan_flag == 0:
                            front_image = front_camera.read()
                            res = driver.go(front_image)
                            if abs(res-0.14) > 0.03 and zhuan_flag == 0:
                                val = 30 * (res-0.14)
                                if val < 10 and val > 0:
                                    val = 10
                                if val > -10 and val <= 0:
                                    val = -10
                                driver.cart.move([val, val, val, val])
                                time.sleep(0.1)
                                driver.cart.move([0, 0, 0, 0])
                                continue
                            elif abs(res-0.14) < 0.03 and zhuan_flag == 0:
                                # driver.cart.move([15, 15, -15, -15])
                                # time.sleep(0.4)
                                driver.cart.move([0, 0, 0, 0])
                                # time.sleep(1)
                                zhuan_flag = 1
                        if len(tasks) > 0 and tasks[0].score > 0.45 and (
                                tasks[0].name == str('putao') or tasks[0].name == str('hetao')):
                            side_image, trade_area, trade_center = draw_res(side_image, tasks)
                            find_trade_flag = 1
                        if find_trade_flag == 1 and zhuan_flag == 1 and up_or_down_flag == 0:
                            for i in range(9):
                                if trade_center[1] < fanwei_down:
                                    up_or_down_list[0] += 1
                                if trade_center[1] > fanwei_up:
                                    up_or_down_list[1] += 1
                                else:
                                    if trade_area > 7500:
                                        #up_or_down = 0
                                        up_or_down_list[0] += 1
                                    else:
                                        #up_or_down = 1
                                        up_or_down_list[1] += 1
                            up_or_down_flag = 1
                        up_or_down = up_or_down_list.index(max(up_or_down_list))
                        print(up_or_down)
                        if up_or_down == 0 and trade_center[0] > 0:
                            if hou_flag == 0:
                                # yy1 = (-3.485879 * 0.000001 * trade_center[0] * trade_center[0] + 5.627056 * 0.001 *
                                #        trade_center[
                                #            0] + 0.265455) if (-3.485879 * 0.000001 * trade_center[
                                #     0] * trade_center[0] + 5.627056 * 0.001 * trade_center[0] + 0.265455) > 0 else 0
                                # yy2 = (-8.8198 * 0.000001 * trade_center[1] * trade_center[1] - 1.90973 * 0.001 *
                                #        trade_center[
                                #            1] + 1.8516266) if (-8.8198 * 0.000001 * trade_center[
                                #     1] * trade_center[1] - 1.90973 * 0.001 + 1.8516266) > 0 else 0
                                hou = (4.1139684 * 0.001 * trade_center[
                                    0] + 0.3971104489) if (4.1139684 * 0.001 * trade_center[
                                    0] + 0.3971104489) > 0 else 0
                                y = -7.031899 * 0.001 * trade_center[1] + 2.6762781
                                if 0 < y < 1:
                                    you = y
                                elif y > 1:
                                    you = y
                                elif y < 0:
                                    you = 0

                                print(hou, you)
                                driver.cart.move([-15, 15, -15, 15])
                                time.sleep(hou)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.1)
                                driver.cart.move([15, 15, -15, -15])
                                time.sleep(you)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.4)
                                moto_stretch.motor_rotate(-20)
                                time.sleep(1.2)  # 1.2
                                moto_stretch.motor_rotate(0)
                                time.sleep(0.5)
                                pwm_clip.servocontrol(50, 30)
                                time.sleep(1)
                                pwm_clip.servocontrol(120, 30)
                                time.sleep(0.2)
                                moto_stretch.motor_rotate(20)
                                time.sleep(1.1)  # 1.1
                                moto_stretch.motor_rotate(0)
                                time.sleep(0.5)
                                hou_flag = 1
                                qian_flag = 0
                            if qian_flag == 0:
                                driver.cart.move([-15, -15, 15, 15])
                                time.sleep(0.75)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.1)
                                driver.cart.move([15, -15, 15, -15])
                                time.sleep(1.15)
                                qian_flag = 1

                            if find_trade_flag == 1 and (abs(trade_center[1] - trade_up_center[1]) < 5 and abs(
                                    trade_center[0] - trade_up_center[0]) < 5) or i == 100:
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(1)
                                servo_lift.servocontrol(25, 75)  # -120
                                time.sleep(1.2)
                                pwm_clip.servocontrol(30, 50)
                                time.sleep(1)
                                moto_stretch.motor_rotate(-20)
                                time.sleep(1.2)  # 1
                                moto_stretch.motor_rotate(0)
                                time.sleep(1)
                                driver.cart.move([15, 15, -15, -15])  # 右
                                time.sleep(0.75)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.5)
                                pwm_clip.servocontrol(120, 30)
                                time.sleep(1)
                                moto_stretch.motor_rotate(20)  # 30
                                time.sleep(1.2)  # 1.2
                                moto_stretch.motor_rotate(0)
                                time.sleep(1)
                                driver.cart.move([-15, -15, 15, 15])  # 左
                                time.sleep(0.65)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.3)
                                servo_lift.servocontrol(-120, 15)  # -120
                                time.sleep(1)
                                break

                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(1)
                                # # time.sleep(1)
                                # driver.cart.move([-20, 20, -20, 20])
                                # time.sleep(1.3)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # driver.cart.move([15, 15, -15, -15])  # 右移
                                # time.sleep(0.65)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # moto_stretch.motor_rotate(-20)
                                # time.sleep(1.2)  # 1.2
                                # moto_stretch.motor_rotate(0)
                                # time.sleep(0.5)
                                # pwm_clip.servocontrol(50, 30)
                                # time.sleep(1)
                                # pwm_clip.servocontrol(120, 30)
                                # time.sleep(0.2)
                                # moto_stretch.motor_rotate(20)
                                # time.sleep(1.2)  # 1.1
                                # moto_stretch.motor_rotate(0)
                                # time.sleep(0.5)
                                # driver.cart.move([-15, -15, 15, 15])  # 左移
                                # time.sleep(0.65)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # driver.cart.move([20, -20, 20, -20])  # 前进
                                # time.sleep(0.95)
                                #
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(1)
                                # servo_lift.servocontrol(8, 75)  # 40
                                # time.sleep(1.2)
                                #
                                # pwm_clip.servocontrol(30, 30)
                                # time.sleep(1)
                                # moto_stretch.motor_rotate(-20)
                                # time.sleep(1.2)  # 1
                                # moto_stretch.motor_rotate(0)
                                # time.sleep(1)
                                # driver.cart.move([15, 15, -15, -15])  # 右移
                                # time.sleep(0.65)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # pwm_clip.servocontrol(120, 30)
                                # time.sleep(1)
                                # moto_stretch.motor_rotate(20)  # 30
                                # time.sleep(1.2)  # 1.2
                                # moto_stretch.motor_rotate(0)
                                # time.sleep(1)
                                # driver.cart.move([-15, -15, 15, 15])  # 左移
                                # time.sleep(0.65)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.3)
                                # servo_lift.servocontrol(-120, 30)  # -120
                                # time.sleep(1.5)
                                # break

                            elif find_trade_flag == 1 and abs(trade_center[1] - trade_up_center[1]) < 5 and trade_center[
                                0] - trade_up_center[0] > 5:
                                driver.cart.move([-15, 15, -15, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and abs(trade_center[1] - trade_up_center[1]) < 5 and trade_center[
                                0] - trade_up_center[0] < -5:
                                driver.cart.move([15, -15, 15, -15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] > 5 and abs(
                                    trade_center[0] - trade_up_center[0]) < 5:
                                driver.cart.move([-15, -15, 15, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] > 5 and trade_center[0] - \
                                    trade_up_center[0] > 5:
                                driver.cart.move([-15, 0, 0, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] > 5 and trade_center[0] - \
                                    trade_up_center[0] < -5:
                                driver.cart.move([0, -15, 15, 0])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] < -5 and abs(
                                    trade_center[0] - trade_up_center[0]) < 5:
                                driver.cart.move([15, 15, -15, -15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] < -5 and trade_center[0] - \
                                    trade_up_center[0] > 5:
                                driver.cart.move([0, 15, -15, 0])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] < -5 and trade_center[0] - \
                                    trade_up_center[0] < -5:
                                driver.cart.move([15, 0, 0, -15])
                                time.sleep(0.1)
                                driver.cart.move([0, 0, 0, 0])
                        if up_or_down == 1 and trade_center[0] > 0:
                            if hou_flag == 0:
                                # y1 = (-2.73 * 0.000001 * trade_center[0] * trade_center[0] + 6.5666 * 0.001 * trade_center[
                                #     0] - 0.1187818) if (-2.73 * 0.000001 * trade_center[0] * trade_center[
                                #     0] + 6.5666 * 0.001 *
                                #                         trade_center[0] - 0.1187818) > 0 else 0
                                # y1 = -1.105 * 10 ** (-21) * trade_center[0] ** 9 + 3.611 * 10 ** (-18) * trade_center[
                                #     0] ** 8 - 4.219 * 10 ** (-15) * trade_center[0] ** 7 + 2.5 * 10**(-12) * trade_center[
                                #            0] ** 6 - 8.48 * 10 ** (-10) * trade_center[0] ** 5 + 1.71 * 10 ** (-7) *trade_center[0] ** 4 - 2.019 * 10 ** (-5) * trade_center[
                                #            0] ** 3 + 0.001282 * trade_center[0] ** 2 - 0.02944 * trade_center[
                                #            0] + 0.1627
                                # y1 = (-2.81228+0.77044*math.log1p(trade_center[0])) if (-2.81228+0.77044*math.log1p(trade_center[0]))>0 else 0
                                # y1 = 1.591756 - 57.60206/trade_center[0]
                                hou = 5.3913808*0.001*trade_center[
                                    0]-0.042856382 if (5.3913808*0.001*trade_center[
                                    0]-0.042856382) > 0 else 0
                                y = -8.301225*0.001*trade_center[1]+4.051346293
                                if 0 < y < 1:
                                    you = y
                                elif y < 0:
                                    you = 0
                                elif y > 1:
                                    you = 1
                                # y2 = (-1.284 * 0.00001 * trade_center[1] * trade_center[1] + 2.11237 * 0.001 * trade_center[
                                #     1] + 1.86677) if (-1.284 * 0.00001 * trade_center[1] * trade_center[
                                #     1] + 2.11237 * 0.001 * trade_center[1] + 1.86677) > 0 else 0
                                print(hou, you)
                                driver.cart.move([-15, 15, -15, 15])
                                time.sleep(hou)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.1)
                                driver.cart.move([15, 15, -15, -15])
                                time.sleep(you)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.4)
                                moto_stretch.motor_rotate(-20)
                                time.sleep(1.2)  # 1.2
                                moto_stretch.motor_rotate(0)
                                time.sleep(0.5)
                                pwm_clip.servocontrol(50, 30)
                                time.sleep(1)
                                pwm_clip.servocontrol(120, 30)
                                time.sleep(0.2)
                                moto_stretch.motor_rotate(20)
                                time.sleep(1.1)  # 1.1
                                moto_stretch.motor_rotate(0)
                                time.sleep(0.5)
                                hou_flag = 1
                                qian_flag = 0
                            if qian_flag == 0:
                                driver.cart.move([-15, -15, 15, 15])
                                time.sleep(0.75)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.1)
                                driver.cart.move([15, -15, 15, -15])
                                time.sleep(1.15)
                                qian_flag = 1
                            if find_trade_flag == 1 and (
                                    abs(trade_center[1] - trade_down_center[1]) < 5 and abs(
                                trade_center[0] - trade_down_center[0]) < 5) or i == 100:
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(1)
                                servo_lift.servocontrol(-120, 30)  # -120
                                time.sleep(1.2)
                                pwm_clip.servocontrol(30, 50)
                                time.sleep(1)
                                moto_stretch.motor_rotate(-20)
                                time.sleep(1.2)  # 1
                                moto_stretch.motor_rotate(0)
                                time.sleep(1)
                                driver.cart.move([15, 15, -15, -15])  # 右
                                time.sleep(0.75)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.5)
                                pwm_clip.servocontrol(120, 30)
                                time.sleep(1)
                                moto_stretch.motor_rotate(20)  # 30
                                time.sleep(1.2)  # 1.2
                                moto_stretch.motor_rotate(0)
                                time.sleep(1)
                                driver.cart.move([-15, -15, 15, 15])  # 左
                                time.sleep(0.65)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.3)
                                break

                                # time.sleep(1)
                                # driver.cart.move([-20, 20, -20, 20])
                                # time.sleep(1.3)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # driver.cart.move([15, 15, -15, -15])  # 右移
                                # time.sleep(0.65)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # moto_stretch.motor_rotate(-20)
                                # time.sleep(1.2)  # 1.2
                                # moto_stretch.motor_rotate(0)
                                # time.sleep(0.5)
                                # pwm_clip.servocontrol(50, 30)
                                # time.sleep(1)
                                # pwm_clip.servocontrol(120, 30)
                                # time.sleep(0.2)
                                # moto_stretch.motor_rotate(20)
                                # time.sleep(1.2)  # 1.1
                                # moto_stretch.motor_rotate(0)
                                # time.sleep(0.5)
                                # driver.cart.move([-15, -15, 15, 15])  # 左移
                                # time.sleep(0.65)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # driver.cart.move([20, -20, 20, -20])
                                # time.sleep(0.95)
                                #
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(1)
                                # servo_lift.servocontrol(-120, 30)  # -120
                                # time.sleep(1.2)
                                #
                                # pwm_clip.servocontrol(30, 30)
                                # time.sleep(1)
                                # moto_stretch.motor_rotate(-20)
                                # time.sleep(1.2)  # 1
                                # moto_stretch.motor_rotate(0)
                                # time.sleep(1)
                                # driver.cart.move([15, 15, -15, -15])  # 右
                                # time.sleep(0.65)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # pwm_clip.servocontrol(120, 30)
                                # time.sleep(1)
                                # moto_stretch.motor_rotate(20)  # 30
                                # time.sleep(1.2)  # 1.2
                                # moto_stretch.motor_rotate(0)
                                # time.sleep(1)
                                # driver.cart.move([-15, -15, 15, 15])  # 左
                                # time.sleep(0.65)
                                # driver.cart.move([0, 0, 0, 0])
                                # time.sleep(0.5)
                                # break


                            elif find_trade_flag == 1 and abs(trade_center[1] - trade_down_center[1]) < 5 and trade_center[
                                0] - trade_down_center[0] > 5:
                                driver.cart.move([-15, 15, -15, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and abs(trade_center[1] - trade_down_center[1]) < 5 and trade_center[
                                0] - trade_down_center[0] < -5:
                                driver.cart.move([15, -15, 15, -15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] > 5 and abs(
                                    trade_center[0] - trade_down_center[0]) < 5:
                                driver.cart.move([-15, -15, 15, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] > 5 and trade_center[0] - \
                                    trade_down_center[0] > 5:
                                driver.cart.move([-15, 0, 0, 15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] > 5 and trade_center[0] - \
                                    trade_down_center[0] < -5:
                                driver.cart.move([0, -15, 15, 0])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] < -5 and abs(
                                    trade_center[0] - trade_down_center[0]) < 5:
                                driver.cart.move([15, 15, -15, -15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] < -5 and trade_center[0] - \
                                    trade_down_center[0] > 5:
                                driver.cart.move([0, 15, -15, 0])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] < -5 and trade_center[0] - \
                                    trade_down_center[0] < -5:
                                driver.cart.move([15, 0, 0, -15])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
            else:
                del (trade_list[0])
                trade_list.append(0)
            if len(signs) > 0 and signs[0].name == "campsite":
                del (campsite_list[0])
                campsite_list.append(1)
                if campsite_list.count(1) > 2 and area > 3500 and area < 24000 and abs(sign_center[1] - 320) < 50:
                    # time.sleep(0.28)
                    time.sleep(0.54)
                    driver.cart.move([0, 0, 0, 0])
                    time.sleep(0.3)
                    driver.cart.Kx = campsite_Kx
                    driver.set_speed(campsite_speed)
                    driver.cart.slow_ratio = 1
                    driver.cart.move([-30, -30, 30, 30])
                    time.sleep(1.6)
                    driver.cart.move([0, 0, 0, 0])
                    time.sleep(0.1)
                    for i in range(3):
                        led.lightcontrol(0, 255, 0, 0)
                        buzzer.rings()
                        time.sleep(0.3)
                        led.lightoff()
                        time.sleep(0.1)
                    driver.cart.move([30, 30, -30, -30])
                    time.sleep(1.6)
                    driver.cart.move([0, 0, 0, 0])
                    time.sleep(0.3)

                    # driver.cruiser.predictor.load(config.cruise_new["model"])
            else:
                del (campsite_list[0])
                campsite_list.append(0)

            print("Kx", driver.cart.Kx)
            # count += 1
            # print(count)

        if cruiser_flag == 1:
            if len(signs) > 0 and signs[0].name == "tower":
                del (tower_list[0])
                tower_list.append(1)
                print(tower_list)
                if tower_list.count(1) > 1 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 180:  #
                    time.sleep(0.65)
                    if tower_num == 1:
                        driver.cart.Kx = tower_Kx_1
                        driver.set_speed(tower_speed_1)
                        driver.cart.slow_ratio = 1
                    if tower_num == 2:
                        driver.cart.Kx = tower_Kx_2
                        driver.set_speed(tower_speed_2)
                        driver.cart.slow_ratio = 1
                        # driver.cruiser.predictor.load(config.cruise["model"])
                    if tower_num == 3:
                        driver.cart.Kx = tower_Kx_3
                        driver.set_speed(tower_speed_3)
                        driver.cart.slow_ratio = 1
                        # driver.cruiser.predictor.load(config.cruise2["model"])
                    tower_num += 1

                    # driver.cruiser.predictor.load(config.cruise["model"])
            else:
                del (tower_list[0])
                tower_list.append(0)

            if len(signs) > 0 and signs[0].name == "protect":
                del (protect_list[0])
                protect_list.append(1)
                if protect_list.count(1) > 1 and sign_center[1] > 260 and abs(
                        sign_center[0] - 320) < 180 and area > 5500:
                    time.sleep(0.8)
                    if protect_num == 1:
                        # driver.cart.move([0,0,0,0])
                        # time.sleep(10)
                        # front_image_s = front_camera.read()
                        # front_image_s[0:240, :] = 0
                        # res = driver.go(front_image_s)
                        black_flag = 1
                        driver.cart.Kx = protect_Kx_1
                        driver.set_speed(protect_speed_1)
                        driver.cruiser.predictor.load(config.cruise3["model"])
                    if protect_num == 2:
                        # front_image = front_camera.read()
                        # res = driver.go(front_image)
                        black_flag = 0
                        driver.cart.Kx = protect_Kx_2
                        driver.set_speed(protect_speed_2)
                        driver.cart.slow_ratio = 1
                        driver.cruiser.predictor.load(config.cruise["model"])
                    if protect_num == 3:
                        driver.cart.Kx = protect_Kx_3
                        driver.set_speed(protect_speed_3)
                        driver.cart.slow_ratio = 1
                        # driver.cruiser.predictor.load(config.cruise["model"])
                        # time.sleep(2)
                    if protect_num == 4:
                        driver.cart.Kx = protect_Kx_4
                        driver.set_speed(protect_speed_4)
                    protect_num += 1
                    # driver.cruiser.predictor.load(config.cruise["model"])
            else:
                del (protect_list[0])
                protect_list.append(0)

            if len(signs) > 0 and signs[0].name == "purchase" and area < 12000:
                del (purchase_list[0])
                purchase_list.append(1)
                if purchase_list.count(1) > 1 and area > 4500:  # 4500
                    time.sleep(0.8)
                    driver.cart.Kx = purchase_Kx
                    driver.set_speed(purchase_speed)

            else:
                del (purchase_list[0])
                purchase_list.append(0)

            if len(signs) > 0 and signs[0].name == "trade" and area > 3500 and area < 12000:
                del (trade_list[0])
                trade_list.append(1)
                if trade_list.count(1) > 1 and area > 6000:
                    time.sleep(0.8)
                    driver.cart.Kx = trade_Kx
                    driver.set_speed(trade_speed)
                    # driver.cruiser.predictor.load(config.cruise["model"])
            else:
                del (trade_list[0])
                trade_list.append(0)

            if len(signs) > 0 and signs[0].name == "campsite":
                del (campsite_list[0])
                campsite_list.append(1)
                if campsite_list.count(1) > 2 and area > 3500 and area < 24000 and abs(sign_center[1] - 320) < 50:
                    time.sleep(0.8)
                    driver.cart.Kx = campsite_Kx
                    driver.set_speed(campsite_speed)
                    driver.cart.slow_ratio = 1
                    # black_flag = 0
                    # driver.cruiser.predictor.load(config.cruise["model"])
            else:
                del (campsite_list[0])
                campsite_list.append(0)

            print("Kx", driver.cart.Kx)


    front_camera.stop()
    # side_camera.stop()




