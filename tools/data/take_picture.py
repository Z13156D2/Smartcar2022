#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
# import numpy as np
# import datetime
import time
#from widgets import Button
#from widegts_test import Buzzer
#from obstacle import Lightwork
#from detectors import Task_Person
#import config
#摄像头编号
#cam = 1  #side
cam = 1   #front
#程序开启运行开关
# start_button = Button(1, "UP")
# #程序关闭开关
# stop_button = Button(1, "DOWN")
camera = cv2.VideoCapture(cam)
camera .set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera .set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
btn = 411
flag = btn

if __name__ == "__main__":
    if cam == 0:
        result_dir = "/run/media/sda1/front_image"
    #cam=1

    else:
        result_dir = "/run/media/sda1/side_image"


    time.sleep(0.2)
    #buz = Buzzer()
    # Lightwork(2, "red")
    # time.sleep(0.2)
    # Lightwork(2, "green")
    # time.sleep(0.2)
    # Lightwork(2, "off")
    print("Start!")
    print('''Press the "Down button" to take photos!''')
    while True:
        # if start_button.clicked():
        #     print(btn)
        #     break
        print("btn", btn)
        path = "{}/{}.png".format(result_dir, btn)
        btn+=1
        time.sleep(0.07)
        return_value, image = camera.read()
        name = "{}.png".format(btn)
        cv2.imwrite(path, image)
        if (btn - flag) == 137:
            break
    #
    # for i in range(3):
    #     buz.rings()
    #     time.sleep(0.3)

    del(camera)

