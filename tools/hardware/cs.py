from detectors import TaskDetector
from detectors import TaskDetector_New
import detectors
from camera import Camera
import config
import time
import cv2

i = 1
tdn = TaskDetector_New()
td = TaskDetector()
side_camera = Camera(config.side_cam, [640, 480])
side_camera.start()
time.sleep(1)
while True:
    side_image = side_camera.read()
    #cv2.imwrite('/home/root/workspace/autostart/src/image/side_image', side_image)
    task, score = tdn.detect(side_image)
    print(task, score)
    #print(score)
    # i = i+1
    # print(i)
    # time.sleep(1)
