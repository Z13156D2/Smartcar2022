import time
from cruiser import Cruiser
from detectors import SignDetector, Trade_two, Task_Purchase, TaskDetector, Task_Person
from camera import Camera
import config
from driver import Driver
from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate, UltrasonicSensor, Buzzer, startmachine
from knn import knn
from img_tool import black_img, draw_res
from tasks import task_tower, identify_bad, hit_person, purchase, trade_up, trade_down, campsite, pur_position


moto_stretch = Motor_rotate(1)
servo_lift = Servo(1)
servo_cam = Servo(2)
driver = Driver()
cruiser = Cruiser()
pwm_clip = Servo_pwm(2)
led = Light(2)
buzzer = Buzzer()
moto2 = Motor_rotate(2)
moto3 = Motor_rotate(3)
uls = UltrasonicSensor(4)

start_button = Button(1, "UP")
stop_button = Button(1, "DOWN")
left_button = Button(1, "LEFT")


trade_up_center = [338, 280]
trade_down_center = [338, 417]
perchase_center_right = [230.0, 417.0]
fanwei_up = 373
fanwei_down = 340

# init
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
person_hight_servo = [0, -5, -50, -80, -90]

if __name__ == "__main__":

    startmachine()
    front_camera = Camera(config.front_cam, [640, 480])
    side_camera = Camera(config.side_cam, [640, 480])
    time.sleep(0.2)
    front_camera.start()
    side_camera.start()
    time.sleep(0.3)
    sd = SignDetector()
    tt = Trade_two()

    tper = Task_Person()


    car_speed = 46
    tower_speed_1 = 60
    tower_speed_2 = 42
    tower_speed_3 = 32
    protect_speed_1 = 30
    protect_speed_2 = 42
    protect_speed_3 = 42
    protect_speed_4 = 55
    campsite_speed = 38
    purchase_speed = 45
    trade_speed = 52

    first_Kx = 1.05

    tower_Kx_1 = 1.08
    tower_Kx_2 = 1.23
    tower_Kx_3 = 1.19
    protect_Kx_1 = 1.98
    protect_Kx_2 = 1.0
    protect_Kx_3 = 1.1
    protect_Kx_4 = 0.9

    purchase_Kx = 1.0
    campsite_Kx = 1.15
    trade_Kx = 0.9

    angle_pid_flag = 0
    driver.set_speed(car_speed)
    driver.cart.Kx = first_Kx
    driver.cart.slow_ratio = 1

    # while True:
    #     if start_button.clicked():
    #         time.sleep(0.3)
    #         break
    #     print("Wait for start!")

    tower_num = 0
    protect_num = 1
    up_or_down = -1
    find_perchase_flag = 0
    bad_person_num = 1
    bad_or_good_list = [0, 0]
    bad_or_good_index = -1
    res_last = 0.0
    res_last_last = 0.0
    black_flag = 0
    while True:

        # if stop_button.clicked():
        #     driver.cart.move([0, 0, 0, 0])
        #     tower_num = 1
        #     target_num = 1
            # while True:
            #     if start_button.clicked():
            #         driver.set_speed(car_speed)
            #         # 转弯系数
            #         driver.cart.Kx = first_Kx # 1.05
            #         # driver.cart.speed_kx = 25
            #         driver.cart.slow_ratio = 1
            #         time.sleep(0.3)
            #         break
            #
            #     print("Wait for start")

        front_image = front_camera.read()
        if black_flag == 1:
            front_image = black_img(front_image)

        res = driver.go(front_image)
        print(res)
        signs, index = sd.detect(front_image)

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


        if len(signs) > 0 and signs[0].name == "tower":
            del (tower_list[0])
            tower_list.append(1)
            if tower_list.count(1) > 1 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 180:

                if tower_num == 1:
                    time.sleep(0.65)
                elif tower_num == 2:
                    time.sleep(0.65)
                elif tower_num == 3:
                    time.sleep(0.65)

                driver.cart.move([0, 0, 0, 0])
                time.sleep(0.1)

                servo_cam.servocontrol(-47, 40)
                time.sleep(2)
                td = TaskDetector()
                time.sleep(0.5)

                find_tower_frame_num = 0
                find_tower_flag = 0
                tasks = [0, 0]
                forward_flag = 0
                backward_flag = 0

                if tower_num == 1:
                    driver.cart.Kx = tower_Kx_1
                    driver.set_speed(tower_speed_1)
                    driver.cart.slow_ratio = 1

                if tower_num == 2:
                    driver.cart.Kx = tower_Kx_2
                    driver.set_speed(tower_speed_2)
                    driver.cart.slow_ratio = 1

                if tower_num == 3:
                    driver.cart.Kx = tower_Kx_3
                    driver.set_speed(tower_speed_3)
                    driver.cart.slow_ratio = 1

                for i in range(30):
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    if len(tasks) > 0 and score > 0.5 and (tasks[0].name == 'alamutu' or tasks[0].name == 'dunhuang' or tasks[0].name == 'jstdb'):

                        find_tower_frame_num += 1

                    if find_tower_frame_num >= 3:

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

                task_tower(tasks[0].name)

                tower_num = tower_num + 1
        else:
            del (tower_list[0])
            tower_list.append(0)

        if len(signs) > 0 and signs[0].name == "protect":
            del (protect_list[0])
            protect_list.append(1)
            if protect_list.count(1) > 2 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 180 and area > 7000:

                if protect_num == 1:
                    time.sleep(0.25)
                    driver.cart.move([0, 0, 0, 0])

                    driver.cart.Kx = protect_Kx_1
                    driver.set_speed(protect_speed_1)
                    driver.cart.slow_ratio = 0.9

                    black_flag = 1
                    driver.cruiser.predictor.load(config.cruise3["model"])

                    driver.cart.move([0, 0, 0, 0])
                    time.sleep(0.5)

                    tper = Task_Person()

                    servo_lift.servocontrol(-120, 15)
                    time.sleep(1.5)

                    bad_or_good_index = identify_bad()
                    print(bad_or_good_index)

                    zhuan_flag = 0
                    valid_num = 0
                    move_flag = 0
                    find_one_in_four_flag = 0
                    high_what = 0
                    person_list_high = [0, 0, 0, 0, 0]

                    for i in range(100):
                        front_image = front_camera.read()
                        side_image = side_camera.read()
                        res = driver.go(front_image)

                        result, score = tper.detect(side_image)
                        frame, area, sign_center = draw_res(side_image, result)
                        print(area, sign_center)

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
                        print("res:", res)
                        print("zhuan_flag", zhuan_flag)
                        print("move_flag", move_flag)
                        if zhuan_flag == 1 and move_flag == 0:
                            if sign_center[0] - 322 < -10:
                                driver.cart.move([-10, 10, -10, 10])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            if sign_center[0] - 322 > 10:
                                driver.cart.move([10, -10, 10, -10])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            if abs(sign_center[0] - 322) < 10:
                                valid_num = valid_num + 1
                            print("valid", valid_num)
                        if zhuan_flag == 1 and valid_num > 5 and move_flag == 0:
                            driver.cart.move([-10, 10, -10, 10])
                            time.sleep(1.09)
                            driver.cart.move([0, 0, 0, 0])
                            move_flag = 1
                        if zhuan_flag == 1 and move_flag == 1 and find_one_in_four_flag == 0:
                            for i in range(8):
                                side_image = side_camera.read()
                                result, score = tper.detect(side_image)
                                distance = uls.read()
                                frame, area, sign_center = draw_res(side_image, result)
                                print(distance, area, sign_center)
                                if type(distance) == int and distance < 30 and len(result) > 0:
                                    # if score > 0.5 and (result[0].name == 'badperson' or result[0].name == 'badperson2'):
                                    this = knn(distance, area, sign_center[1])
                                    person_list_high[this] = person_list_high[this] + 1
                                print("person_list_high", person_list_high)
                            high_what = person_list_high.index(max(person_list_high))
                            person_hight_record.append(high_what)
                            find_one_in_four_flag = 1
                            if bad_or_good_index == 0:
                                break

                        if bad_or_good_index == 1 and high_what == 1:
                            hit_person(high_what)
                            bad_person_num += 1
                            break
                        elif bad_or_good_index == 1 and high_what == 2:
                            hit_person(high_what)
                            time.sleep(1)
                            bad_person_num += 1
                            break
                        elif bad_or_good_index == 1 and high_what == 3:
                            hit_person(high_what)
                            bad_person_num += 1
                            break
                        elif bad_or_good_index == 1 and (high_what == 4 or i == 99):
                            high_what = 4
                            hit_person(high_what)
                            bad_person_num += 1
                            break

                if protect_num == 2:
                    time.sleep(0.53)
                    driver.cart.Kx = protect_Kx_2
                    driver.set_speed(protect_speed_2)
                    driver.cart.slow_ratio = 1
                    black_flag = 0
                    driver.cruiser.predictor.load(config.cruise["model"])
                    # if bad_person_num <= 2:
                    # driver.cart.move([10,-10,10,-10])
                    # time.sleep(0.9)

                    driver.cart.move([0, 0, 0, 0])
                    time.sleep(0.5)
                    # servo_cam.servocontrol(-47, 40)
                    # time.sleep(1.0)
                    servo_lift.servocontrol(-120, 10)
                    time.sleep(0.5)
                    bad_or_good_list = [0, 0]
                    zhuan_flag = 0
                    for i in range(30):
                        front_image = front_camera.read()
                        res = driver.go(front_image)
                        if abs(res + 0.33) > 0.02:
                            val = 30 * (res - 0.3)
                            if val < 10 and val > 0:
                                val = 10
                            if val > -10 and val <= 0:
                                val = -10
                            driver.cart.move([val, val, val, val])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                            continue
                        elif abs(res + 0.33) < 0.02:
                            driver.cart.move([0, 0, 0, 0])
                            zhuan_flag = 1
                            # time.sleep(1)
                            break

                    # driver.cart.move([15, -15, 15, -15])
                    # time.sleep(1.)
                    driver.cart.move([0, 0, 0, 0])
                    time.sleep(0.3)

                    # if sign_center[0] == 0:
                    #     driver.cart.move([10, -10, 10, -10])
                    #     time.sleep(0.8)
                    for i in range(11):
                        side_image = side_camera.read()
                        result, score = tper.detect(side_image)
                        if len(result) > 0:
                            print("name", result[0].name, "score", score)
                        else:
                            print("laji")

                        if len(result) > 0 and (result[0].name == 'badperson' or result[0].name == 'badperson2'):
                            bad_or_good_list[0] = bad_or_good_list[0] + 1
                        if len(result) > 0 and (result[0].name == 'goodperson' or result[0].name == 'goodperson2'):
                            bad_or_good_list[1] = bad_or_good_list[1] + 1
                        print("bad_or_good_list", bad_or_good_list)
                    bad_or_good_index = bad_or_good_list.index(max(bad_or_good_list))
                    print("bad_or_good_index", bad_or_good_index)
                    #zhuan_flag = 0
                    valid_num = 0
                    move_flag = 0
                    find_one_in_four_flag = 0
                    high_what = 0
                    person_list_high = [0, 0, 0, 0, 0]
                    front_flag = 0
                    # if bad_or_good_index == 0:
                    # servo_lift.servocontrol(-100, 30)
                    # -120

                    for i in range(100):
                        front_image = front_camera.read()
                        side_image = side_camera.read()
                        res = driver.go(front_image)
                        print(res)
                        result, score = tper.detect(side_image)
                        frame, area, sign_center = draw_res(side_image, result)

                        print("res", res)
                        print("zhuang_flag", zhuan_flag)
                        if zhuan_flag == 1 and move_flag == 0:
                            if sign_center[0] - 322 < -10:
                                driver.cart.move([-10, 10, -10, 10])
                                time.sleep(0.12)
                                print('!!!!!!!!!!!!!!!!')
                                driver.cart.move([0, 0, 0, 0])
                            if sign_center[0] - 322 > 10:
                                driver.cart.move([10, -10, 10, -10])
                                time.sleep(0.12)
                                print("!!!!!!!!!!!!!!!!")
                                driver.cart.move([0, 0, 0, 0])
                            if abs(sign_center[0] - 322) < 10:
                                valid_num = valid_num + 1
                            print("valid_number", valid_num)

                        if zhuan_flag == 1 and valid_num > 4 and move_flag == 0:
                            driver.cart.move([-10, 10, -10, 10])
                            time.sleep(1.15)
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
                                if type(distance) == int and distance < 30 and len(result) > 0:
                                    # if score > 0.5 and (result[0].name == 'badperson' or result[0].name == 'badperson2'):
                                    this = knn(distance, area, sign_center[1])
                                    person_list_high[this] = person_list_high[this] + 1
                                print("person_list_high", person_list_high)
                            high_what = person_list_high.index(max(person_list_high))
                            print("high_what", high_what)
                            person_hight_record.append(high_what)
                            find_one_in_four_flag = 1
                            if bad_or_good_index == 1:
                                break

                        if bad_or_good_index == 0 and high_what == 1:
                            hit_person(high_what)
                            bad_person_num += 1
                            break
                        elif bad_or_good_index == 0 and high_what == 2:
                            hit_person(high_what)
                            bad_person_num += 1
                            break
                        elif bad_or_good_index == 0 and (high_what == 3 or i == 99):
                            high_what = 3
                            hit_person(high_what)
                            bad_person_num += 1
                            break
                        elif bad_or_good_index == 0 and high_what == 4:
                            hit_person(high_what)
                            bad_person_num += 1
                            break
                if protect_num == 3:
                    time.sleep(0.6)
                    driver.cart.Kx = protect_Kx_1
                    driver.set_speed(protect_speed_1)
                    driver.cart.slow_ratio = 1
                    driver.cruiser.predictor.load(config.cruise["model"])
                    # if bad_person_num <= 2:
                    driver.cart.move([0, 0, 0, 0])
                    time.sleep(0.5)
                    # servo_cam.servocontrol(-47, 40)
                    # time.sleep(1.0)
                    servo_lift.servocontrol(-120, 30)
                    time.sleep(1.5)
                    bad_or_good_list = [0, 0]
                    for i in range(21):
                        side_image = side_camera.read()
                        result, score = tper.detect(side_image)
                        if len(result) > 0 and (result[0].name == 'badperson' or result[0].name == 'badperson2'):
                            bad_or_good_list[0] = bad_or_good_list[0] + 1
                        if len(result) > 0 and (result[0].name == 'goodperson' or result[0].name == 'goodperson2'):
                            bad_or_good_list[1] = bad_or_good_list[1] + 1
                        print(bad_or_good_list)
                    bad_or_good_index = bad_or_good_list.index(max(bad_or_good_list))
                    zhuan_flag = 0
                    valid_num = 0
                    move_flag = 0
                    find_one_in_four_flag = 0
                    high_what = 0
                    person_list_high = [0, 0, 0, 0, 0]
                    # if bad_or_good_index == 0:
                    # servo_lift.servocontrol(-100, 30)
                    # -120
                    for i in range(100):
                        front_image = front_camera.read()
                        side_image = side_camera.read()
                        res = driver.go(front_image)
                        result, score = tper.detect(side_image)
                        frame, area, sign_center = draw_res(side_image, result)
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
                        if zhuan_flag == 1 and move_flag == 0:
                            if sign_center[0] - 322 < -5:
                                driver.cart.move([-10, 10, -10, 10])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            if sign_center[0] - 322 > 5:
                                driver.cart.move([10, -10, 10, -10])
                                time.sleep(0.07)
                                driver.cart.move([0, 0, 0, 0])
                            if abs(sign_center[0] - 322) < 5:
                                valid_num = valid_num + 1
                        if zhuan_flag == 1 and valid_num > 5 and move_flag == 0:
                            driver.cart.move([-10, 10, -10, 10])
                            time.sleep(1.19)
                            driver.cart.move([0, 0, 0, 0])
                            move_flag = 1
                        if zhuan_flag == 1 and move_flag == 1 and find_one_in_four_flag == 0:
                            for i in range(8):
                                side_image = side_camera.read()
                                result, score = tper.detect(side_image)
                                distance = uls.read()
                                frame, area, sign_center = draw_res(side_image, result)
                                print(distance, area, sign_center)
                                if type(distance) == int and distance < 30 and len(result) > 0:
                                    # if score > 0.5 and (result[0].name == 'badperson' or result[0].name == 'badperson2'):
                                    this = knn(distance, area, sign_center[1])
                                    person_list_high[this] = person_list_high[this] + 1
                            high_what = person_list_high.index(max(person_list_high))
                            person_hight_record.append(high_what)
                            find_one_in_four_flag = 1
                            if bad_or_good_index == 1:
                                break

                        if bad_person_num < 3:

                            if bad_or_good_index == 0 and (high_what == 1 or i == 99):
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == 0 and high_what == 2:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == 0 and high_what == 3:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                            elif bad_or_good_index == 0 and high_what == 4:
                                hit_person(high_what)
                                bad_person_num += 1
                                break
                if protect_num == 4:
                    # time.sleep(0.93)
                    driver.cart.Kx = protect_Kx_4
                    driver.set_speed(protect_speed_4)
                    driver.cruiser.predictor.load(config.cruise["model"])
                    if bad_person_num <= 2:
                        time.sleep(0.3)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(0.5)
                        servo_cam.servocontrol(122, 40)
                        time.sleep(1.5)
                        protect_4_hight_index = [high_index for high_index in person_hight_stand if
                                                 high_index not in person_hight_record]
                        protect_4_hight = person_hight_servo[protect_4_hight_index[0]]
                        for i in range(100):
                            front_image = front_camera.read()
                            side_image = side_camera.read()
                            res = driver.go(front_image)
                            result, score = tper.detect(side_image)
                            frame, area, sign_center = draw_res(side_image, result)
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

                            if len(result) > 0:
                                if zhuan_flag == 1 and (
                                        result[0].name == 'badperson' or result[0].name == 'badperson2'):
                                    if sign_center[0] - 322 < -5:
                                        driver.cart.move([-10, 10, -10, 10])
                                        time.sleep(0.07)
                                        driver.cart.move([0, 0, 0, 0])
                                    if sign_center[0] - 322 > 5:
                                        driver.cart.move([10, -10, 10, -10])
                                        time.sleep(0.07)
                                        driver.cart.move([0, 0, 0, 0])
                                    if abs(sign_center[0] - 322) < 5:
                                        valid_num = valid_num + 1
                            if zhuan_flag == 1 and valid_num > 5:
                                driver.cart.move([-10, 10, -10, 10])
                                time.sleep(3.)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(0.5)
                                servo_lift.servocontrol(protect_4_hight, 50)
                                time.sleep(1.8)
                                moto3.motor_rotate(-15)
                                time.sleep(4.9)
                                moto3.motor_rotate(0)
                                time.sleep(1)
                                moto3.motor_rotate(15)
                                time.sleep(4.9)
                                moto3.motor_rotate(0)
                                time.sleep(0.5)
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
            if purchase_list.count(1) > 1 and area > 4500:  # 4500
                time.sleep(0.7)
                driver.cart.move([0, 0, 0, 0])
                driver.cart.Kx = purchase_Kx
                driver.set_speed(purchase_speed)
                servo_cam.servocontrol(122, 40)
                time.sleep(1)
                zhuan_flag = 0
                find_right_flag = 0
                position_flag = 0
                forward_flag = 0
                backward_flag = 0
                tp = Task_Purchase()
                time.sleep(1)
                find_right_flag_once = 0
                perchase_right_list = [0, 0, 0, 0, 0, 0]
                move_position_list = [0, 0, 0, 0, 0, 0]
                for i in range(101):

                    front_image = front_camera.read()
                    side_image = side_camera.read()

                    tasks, score, origin= tp.detect(side_image)
                    print(tasks, score)
                    res = driver.go(front_image)

                    if abs(res + 0.26) > 0.07 and zhuan_flag == 0:
                        val = 30 * (res + 0.26)
                        if val < 10 and val > 0:
                            val = 10
                        if val > -10 and val <= 0:
                            val = -10
                        driver.cart.move([val, val, val, val])
                        time.sleep(0.1)
                        driver.cart.move([0,0,0,0])

                        continue
                    elif abs(res + 0.26) < 0.07 and zhuan_flag == 0:
                        driver.cart.move([0, 0, 0, 0])
                        # time.sleep(1)
                        zhuan_flag = 1


                    if position_flag == 0 and zhuan_flag ==1:
                        tf, x_mean = pur_position(origin)
                        if tf == 1:
                            del (move_position_list[0])
                            move_position_list.append(1)
                        if tf == 0 and x_mean < 320:
                            driver.cart.move([20, -20, 20, -20])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                            del (move_position_list[0])
                            move_position_list.append(0)
                        if tf == 0 and x_mean >= 320:
                            driver.cart.move([-20, 20, -20, 20])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                            del (move_position_list[0])
                            move_position_list.append(0)
                        if tf == -1:
                            if forward_flag == 0:
                                driver.cart.move([10, -10, 10, -10])
                                time.sleep(1)
                                driver.cart.move([0, 0, 0, 0])
                                forward_flag = 1



                    if move_position_list.count(1) > 2:
                        position_flag = 1


                    if len(tasks) > 0 and position_flag == 1:
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

                    if find_right_flag == 0 and max(perchase_right_list) > 3:
                        right_target_name = config.purchase_list[perchase_right_list.index(max(perchase_right_list))]
                        find_right_flag = 1

                    if len(tasks) > 0 and tasks[0].score > 0.4 and find_right_flag == 1 and tasks[
                        0].name == right_target_name:
                        side_image, perchase_area, perchase_center = draw_res(side_image, tasks)
                        find_right_flag_once = 1

                    if find_right_flag_once == 1:

                        if (abs(perchase_center[1] - perchase_center_right[1]) < 5 and abs(
                                perchase_center[0] - perchase_center_right[0]) < 5) or i == 100:
                            purchase()
                            break
                            # pwm_clip.servocontrol(0, 30)
                            # time.sleep(1)

                            # time.sleep(10000)

                        elif abs(perchase_center[1] - perchase_center_right[1]) < 5 and perchase_center[0] - \
                                perchase_center_right[0] > 5:
                            driver.cart.move([-10, 10, -10, 10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif abs(perchase_center[1] - perchase_center_right[1]) < 5 and perchase_center[0] - \
                                perchase_center_right[0] < -5:
                            driver.cart.move([10, -10, 10, -10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif perchase_center[1] - perchase_center_right[1] > 5 and abs(
                                perchase_center[0] - perchase_center_right[0]) < 5:
                            driver.cart.move([-10, -10, 10, 10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif perchase_center[1] - perchase_center_right[1] > 5 and perchase_center[0] - \
                                perchase_center_right[0] > 5:
                            driver.cart.move([-15, 0, 0, 15])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif perchase_center[1] - perchase_center_right[1] > 5 and perchase_center[0] - \
                                perchase_center_right[0] < -5:
                            driver.cart.move([0, -15, 15, 0])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif perchase_center[1] - perchase_center_right[1] < -5 and abs(
                                perchase_center[0] - perchase_center_right[0]) < 5:
                            driver.cart.move([10, 10, -10, -10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif perchase_center[1] - perchase_center_right[1] < -5 and perchase_center[0] - \
                                perchase_center_right[0] > 5:
                            driver.cart.move([0, 15, -15, 0])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif perchase_center[1] - perchase_center_right[1] < -5 and perchase_center[0] - \
                                perchase_center_right[0] < -5:
                            driver.cart.move([15, 0, 0, -15])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])


        else:
            del (purchase_list[0])
            purchase_list.append(0)

        if len(signs) > 0 and signs[0].name == "trade" and area > 3500 and area < 12000:
            del (trade_list[0])
            trade_list.append(1)
            if trade_list.count(1) > 1 and area > 6000:
                time.sleep(0.9)
                driver.cart.move([0, 0, 0, 0])
                driver.cart.Kx = trade_Kx
                # driver.cart.move([-10, -10, 10, 10])
                # time.sleep(0.8)
                # driver.cart.move([0, 0, 0, 0])
                tt = Trade_two()
                driver.set_speed(trade_speed)
                # driver.cruiser.predictor.load(config.cruise["model"])
                # 摄像头舵机
                time.sleep(0.7)
                servo_cam.servocontrol(122, 40)
                time.sleep(3)

                zhuan_flag = 0
                not_find_flag = 0
                for i in range(101):
                    front_image = front_camera.read()
                    side_image = side_camera.read()
                    #front_image = black_img(front_image)
                    # side_image = side_camera.read()
                    tasks, score = tt.detect(side_image)
                    print(tasks, score)
                    res = driver.go(front_image)
                    # res = driver.go(front_image)
                    # if abs(res) > 0.2:
                    #     res = 0
                    # driver.set_speed(10)
                    # find_trade_flag = 0
                    if len(tasks) > 0 and tasks[0].score > 0.4 and (
                            tasks[0].name == str('putao') or tasks[0].name == str('hetao')):
                        side_image, trade_area, trade_center = draw_res(side_image, tasks)
                        find_trade_flag = 1

                    if abs(res) > 0.07 and zhuan_flag == 0:
                        val = 30 * (res)
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
                    if find_trade_flag == 1 and zhuan_flag == 1 and up_or_down_flag == 0:
                        if trade_center[1] < fanwei_up:
                            up_or_down = 0
                        if trade_center[1] > fanwei_down:
                            up_or_down = 1
                        else:
                            if trade_area > 10000:
                                up_or_down = 0
                            else:
                                up_or_down = 1
                        up_or_down_flag = 1
                    if up_or_down == 0:
                        if find_trade_flag == 1 and (
                                abs(trade_center[1] - trade_up_center[1]) < 5 and abs(
                            trade_center[0] - trade_up_center[0]) < 5) or i == 100:
                            trade_up()
                            break
                            # pwm_clip.servocontrol(0, 30)
                            # time.sleep(1)

                            # time.sleep(10000)

                        elif find_trade_flag == 1 and abs(trade_center[1] - trade_up_center[1]) < 5 and trade_center[
                            0] - trade_up_center[0] > 5:
                            driver.cart.move([-10, 10, -10, 10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and abs(trade_center[1] - trade_up_center[1]) < 5 and trade_center[
                            0] - trade_up_center[0] < -5:
                            driver.cart.move([10, -10, 10, -10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] > 5 and abs(
                                trade_center[0] - trade_up_center[0]) < 5:
                            driver.cart.move([-10, -10, 10, 10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] > 5 and trade_center[0] - \
                                trade_up_center[0] > 5:
                            driver.cart.move([-15, 0, 0, 15])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] > 5 and trade_center[0] - \
                                trade_up_center[0] < -5:
                            driver.cart.move([0, -15, 15, 0])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] < -5 and abs(
                                trade_center[0] - trade_up_center[0]) < 5:
                            driver.cart.move([10, 10, -10, -10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] < -5 and trade_center[0] - \
                                trade_up_center[0] > 5:
                            driver.cart.move([0, 15, -15, 0])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_up_center[1] < -5 and trade_center[0] - \
                                trade_up_center[0] < -5:
                            driver.cart.move([15, 0, 0, -15])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                    if up_or_down == 1:
                        if find_trade_flag == 1 and (
                                abs(trade_center[1] - trade_down_center[1]) < 5 and abs(
                            trade_center[0] - trade_down_center[0]) < 5) or i == 100:

                            trade_down()
                            break

                        elif find_trade_flag == 1 and abs(trade_center[1] - trade_down_center[1]) < 5 and trade_center[
                            0] - trade_down_center[0] > 5:
                            driver.cart.move([-10, 10, -10, 10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and abs(trade_center[1] - trade_down_center[1]) < 5 and trade_center[
                            0] - trade_down_center[0] < -5:
                            driver.cart.move([10, -10, 10, -10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] > 5 and abs(
                                trade_center[0] - trade_down_center[0]) < 5:
                            driver.cart.move([-10, -10, 10, 10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] > 5 and trade_center[0] - \
                                trade_down_center[0] > 5:
                            driver.cart.move([-15, 0, 0, 15])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] > 5 and trade_center[0] - \
                                trade_down_center[0] < -5:
                            driver.cart.move([0, -15, 15, 0])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] < -5 and abs(
                                trade_center[0] - trade_down_center[0]) < 5:
                            driver.cart.move([10, 10, -10, -10])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] < -5 and trade_center[0] - \
                                trade_down_center[0] > 5:
                            driver.cart.move([0, 15, -15, 0])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
                        elif find_trade_flag == 1 and trade_center[1] - trade_down_center[1] < -5 and trade_center[0] - \
                                trade_down_center[0] < -5:
                            driver.cart.move([15, 0, 0, -15])
                            time.sleep(0.1)
                            driver.cart.move([0, 0, 0, 0])
        else:
            del (trade_list[0])
            trade_list.append(0)

        if len(signs) > 0 and signs[0].name == "campsite":
            del (campsite_list[0])
            campsite_list.append(1)
            if campsite_list.count(1) > 2 and area > 3500 and area < 24000 and abs(sign_center[1] - 320) < 50:
                # time.sleep(0.28)
                time.sleep(0.6)
                driver.cart.move([0, 0, 0, 0])
                time.sleep(0.9)
                driver.cart.Kx = campsite_Kx
                driver.set_speed(campsite_speed)
                driver.cart.slow_ratio = 1
                campsite()

                # driver.cruiser.predictor.load(config.cruise_new["model"])
        else:
            del (campsite_list[0])
            campsite_list.append(0)

        print("Kx", driver.cart.Kx)
        # count += 1
        # print(count)
    front_camera.stop()




