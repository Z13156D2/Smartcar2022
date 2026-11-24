#from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate, UltrasonicSensor, Buzzer, Light
import time
from detectors import Task_Person, Trade_two, res_to_detection
from camera import Camera
import config
from driver import Driver



moto2 = Motor_rotate(2)
moto_stretch = Motor_rotate(1)
led = Light(2)
servo_lift = Servo(1)
moto3 = Motor_rotate(3)
hit_right = Motor_rotate(4)
hit_left = Servo_pwm(6)
pwm_clip = Servo_pwm(2)
buzzer = Buzzer()


driver = Driver()


def task_tower(flag_name):
    if flag_name == "dunhuang":
        moto2.motor_rotate(-10)
        time.sleep(0.8)  # 初到左
        moto2.motor_rotate(0)
        time.sleep(0.2)
        for i in range(3):
            led.lightcontrol(2, 0, 255, 0)
            led.lightoff()
        moto2.motor_rotate(10)
        time.sleep(0.7)
        moto2.motor_rotate(0)
    elif flag_name == "alamutu":
        moto2.motor_rotate(10)
        time.sleep(0.6)  # 初到右
        moto2.motor_rotate(0)
        time.sleep(0.2)
        for i in range(3):
            led.lightcontrol(2, 0, 255, 0)
            led.lightoff()
        moto2.motor_rotate(-10)
        time.sleep(0.5)
        moto2.motor_rotate(0)
    elif flag_name == "jstdb":
        moto2.motor_rotate(10)
        time.sleep(1.3)  # 初到中
        moto2.motor_rotate(0)
        time.sleep(0.2)
        for i in range(3):
            led.lightcontrol(2, 0, 255, 0)
            led.lightoff()
        moto2.motor_rotate(-10)
        time.sleep(1.18)
        moto2.motor_rotate(0)


def identify_bad(side_camera):
    tper = Task_Person()
    bad_or_good_list = [0, 0]
    # side_camera = Camera(config.side_cam, [640, 480])
    # side_camera.start()
    for i in range(9):
        side_image = side_camera.read()
        result, score = tper.detect(side_image)
        if len(result) > 0 and (result[0].name == 'badperson' or result[0].name == 'badperson2'):
            bad_or_good_list[1] = bad_or_good_list[1] + 1
        if len(result) > 0 and (result[0].name == 'goodperson' or result[0].name == 'goodperson2'):
            bad_or_good_list[0] = bad_or_good_list[0] + 1
        if len(result) == 0:
            pass
        print(bad_or_good_list)

    if (bad_or_good_list[0] + bad_or_good_list[1]) < 3 or bad_or_good_list[0] == bad_or_good_list[1]:
        return "0"
    bad_or_good_index = bad_or_good_list.index(max(bad_or_good_list))

    if bad_or_good_index == 0:
        return "good"
    elif bad_or_good_index == 1:
        return "bad"


def hit_person(high_what):
    person_hight_servo = [0, 25, -20, -50, -80]
    hight = person_hight_servo[high_what]

    driver.cart.move([-20, 20, -20, 20])
    time.sleep(0.4)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(1)
    servo_lift.servocontrol(hight, 70)
    time.sleep(2)
    hit_left.servocontrol(60, 90)
    time.sleep(2)
    hit_left.servocontrol(-75, 90)
    time.sleep(2)
    # moto3.motor_rotate(-55)
    # time.sleep(1.75)
    # moto3.motor_rotate(0)
    # time.sleep(1)
    # moto3.motor_rotate(55)
    # time.sleep(0.99)
    # moto3.motor_rotate(0)
    # time.sleep(0.5)
    servo_lift.servocontrol(-120, 10)  # -120
    time.sleep(1)



def purchase():
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.4)
    servo_lift.servocontrol(-75, 70)  # -60
    time.sleep(1)
    pwm_clip.servocontrol(48, 30)
    time.sleep(1)
    moto_stretch.motor_rotate(-20)
    time.sleep(1.2)
    moto_stretch.motor_rotate(0)
    time.sleep(1)
    pwm_clip.servocontrol(124, 50)
    time.sleep(1.5)
    servo_lift.servocontrol(-50, 70)  # -45
    time.sleep(0.9)
    moto_stretch.motor_rotate(20)
    time.sleep(1.2)
    moto_stretch.motor_rotate(0)
    time.sleep(1.8)
    driver.cart.move([-15, -15, 15, 15])
    time.sleep(0.3)


def trade_up():
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.4)

    # time.sleep(1)
    driver.cart.move([-20, 20, -20, 20])
    time.sleep(1.3)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    driver.cart.move([15, 15, -15, -15])  # 右移
    time.sleep(0.68)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    moto_stretch.motor_rotate(-20)
    time.sleep(1.2)  # 1.2
    moto_stretch.motor_rotate(0)
    time.sleep(0.5)
    pwm_clip.servocontrol(50, 30)
    time.sleep(1)
    pwm_clip.servocontrol(120, 30)
    time.sleep(0.2)
    moto_stretch.motor_rotate(20)
    time.sleep(1.2)  # 1.1
    moto_stretch.motor_rotate(0)
    time.sleep(0.5)
    driver.cart.move([-15, -15, 15, 15])  # 左移
    time.sleep(0.68)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    driver.cart.move([20, -20, 20, -20])  # 前进
    time.sleep(0.95)

    driver.cart.move([0, 0, 0, 0])
    time.sleep(1)
    servo_lift.servocontrol(25, 75)  # 40
    time.sleep(1.2)

    pwm_clip.servocontrol(30, 30)
    time.sleep(1)
    moto_stretch.motor_rotate(-20)
    time.sleep(1.2)  # 1
    moto_stretch.motor_rotate(0)
    time.sleep(1)
    driver.cart.move([15, 15, -15, -15])  # 右移
    time.sleep(0.68)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    pwm_clip.servocontrol(120, 30)
    time.sleep(1)
    moto_stretch.motor_rotate(20)  # 30
    time.sleep(1.2)  # 1.2
    moto_stretch.motor_rotate(0)
    time.sleep(1)
    driver.cart.move([-15, -15, 15, 15])  # 左移
    time.sleep(0.68)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.3)
    servo_lift.servocontrol(-120, 30)  # -120
    time.sleep(1.5)


def trade_down():
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)

    # time.sleep(1)
    driver.cart.move([-20, 20, -20, 10])
    time.sleep(3.2)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    driver.cart.move([10, 10, -10, -10])  # 右移
    time.sleep(1.2)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    moto_stretch.motor_rotate(-20)
    time.sleep(1.2)  # 1.2
    moto_stretch.motor_rotate(0)
    time.sleep(0.5)
    pwm_clip.servocontrol(50, 30)
    time.sleep(1)
    pwm_clip.servocontrol(120, 30)
    time.sleep(0.2)
    moto_stretch.motor_rotate(20)
    time.sleep(1.2)  # 1.1
    moto_stretch.motor_rotate(0)
    time.sleep(0.5)
    driver.cart.move([-15, -15, 15, 15])  # 左移
    time.sleep(0.68)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    driver.cart.move([20, -20, 20, -20])
    time.sleep(0.95)

    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    servo_lift.servocontrol(-120, 15)  # -120
    time.sleep(1.2)

    pwm_clip.servocontrol(30, 30)
    time.sleep(1)
    moto_stretch.motor_rotate(-20)
    time.sleep(1.2)  # 1
    moto_stretch.motor_rotate(0)
    time.sleep(1)
    driver.cart.move([15, 15, -15, -15])  # 右
    time.sleep(0.68)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)
    pwm_clip.servocontrol(120, 30)
    time.sleep(1)
    moto_stretch.motor_rotate(20)  # 30
    time.sleep(1.2)  # 1.2
    moto_stretch.motor_rotate(0)
    time.sleep(1)
    driver.cart.move([-15, -15, 15, 15])  # 左
    time.sleep(0.68)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.5)


def campsite():
    driver.cart.move([-30, -30, 30, 30])
    time.sleep(1.6)
    driver.cart.move([0, 0, 0, 0])
    for i in range(3):
        led.lightcontrol(2, 255, 0, 0)
        buzzer.rings()
        time.sleep(0.3)
        led.lightoff()
    driver.cart.move([30, 30, -30, -30])
    time.sleep(1.6)
    driver.cart.move([0, 0, 0, 0])
    time.sleep(0.3)


def pur_position(result):

    position_flag = -1
    wight = 640
    x_sum = 0

    #threshold = config.purchase_list["threshold"]

    record_list = [0, 0, 0, 0, 0, 0]
    box_array = []
    if len(result) == 0:
        return -1, 0

    for box in result:
        if box[1] > 0.4:
            record_list[int(box[0])] = record_list[int(box[0])] + 1
            box_array.append(box)

    if len(box_array) == 0:
        return -1, 0.

    max_num = max(record_list)
    record_list[record_list.index(max(record_list))] = 0

    if max_num > 1 and max(record_list) > 0:
        position_flag = 1
    else:
        position_flag = 0

    for item in box_array:
        x_1 = item[2] * wight
        x_2 = item[4] * wight
        x_c = (x_1 + x_2) / 2
        x_sum = x_sum + x_c

    x_meam = x_sum / len(box_array)

    return position_flag, x_meam









