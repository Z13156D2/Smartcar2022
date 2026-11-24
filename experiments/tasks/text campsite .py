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
        if len(signs) > 0 and signs[0].name == "campsite":
            btn += 1
            front_image, target_area, target_center = draw_res(front_image, signs, btn)
            del (campsite_list[0])
            campsite_list.append(1)
            if campsite_list.count(1) > 1 and area > 3500 and area < 24000 and abs(sign_center[1] - 320) < 50:#270< y <370
                btn += 1
                front_image, target_area, target_center = draw_res(front_image, signs, btn)
                time.sleep(0.3)#0.4
                driver.cart.move([0, 0, 0, 0])
                time.sleep(0.3)
                driver.cart.move([-15, -15, 15, 15])
                time.sleep(3.2)
                driver.cart.move([0, 0, 0, 0])
                time.sleep(3)
                driver.cart.move([15, 15, -15, -15])
                time.sleep(3.2)
                driver.cart.move([0, 0, 0, 0])
                time.sleep(1)
        else:
            del (campsite_list[0])
            campsite_list.append(0)
for i in range(10):  # 闪灯三次
    led.lightcontrol(2, 255, 0, 0)  # 2号亮红灯
    time.sleep(0.2)
    led.lightoff()

