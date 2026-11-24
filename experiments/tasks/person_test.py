from detectors import Task_Person
from detectors import TaskDetector_New
#from detectors import SignDetector_New
from detectors import SignDetector, TaskDetector, SignDetector_New, Task_Person, Task_Purchase, TaskDetector_Ban, Trade_two, Task_Purchase_1
from camera import Camera
import config
import time
import cv2
#from widgets_servo_test import UltrasonicSensor
#from knn import knn
#from widegts_test import Buzzer


#uls = UltrasonicSensor(4)


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




def black_img(frame):
    # frame[0:80][0:640] = 0
    frame[0:250][0:640] = 0
    return frame


side_cam = Camera(config.front_cam, [640, 480])
side_cam.start()
time.sleep(0.2)
tp = Task_Purchase()
#tn = TaskDetector_New()
sd = SignDetector()
#sdn = SignDetector_New()
tt = Trade_two()
#sd = SignDetector()
tdn = TaskDetector_New()
td = TaskDetector()
tper = Task_Person()
tp1 = Task_Purchase_1()
#tdb = TaskDetector_Ban()
time.sleep(0.2)
i = 1
fanwei_up = 373
fanwei_down = 340
up_or_down = -1
while True:
    side_img = side_cam.read()
    # side_img = black_img(side_img)
    result, b = tp.detect(side_img)
    print(result, b)

    # if len(result) > 0:
    #     print(result, b[0].name)
    # if len(result) > 0:
    #     frame, area, sign_center = draw_res(side_img, result)
    #     print(area, sign_center)
    # #
    # #     hight = knn(d, area, sign_center[1])
    # #     print(hight)
    # #
    # # else:
    # #    print("laji")
    # else:
    #
    #     print("laji")
    #
    #     if sign_center[1] < 328:#199-385
    #         up_or_down = 0
    #     if sign_center[1] > 385:#328-455
    #         up_or_down = 1
    #     else:
    #         if area > 7500:
    #             up_or_down = 0
    #         else:
    #             up_or_down = 1
    #
    #     print("!!!!!!!!!!!!!!!", up_or_down)
    # else:
    #     print("laji")
    # # # #print(result, b)

