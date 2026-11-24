from driver import Driver
import time
import cv2
from opencv_tool import draw_line, draw_res


# cam = 1  # side
cam = 0   # front

camera = cv2.VideoCapture(cam)
camera .set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera .set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
driver = Driver()

btn = 0
flag = btn

if __name__ == "__main__":
    if cam == 0:
        result_dir = "/run/media/sda1/front_image"
    else:
        result_dir = "/run/media/sda1/side_image"

    time.sleep(0.2)

    print("Start!")

    while True:

        print("btn", btn)
        path = "{}/{}.png".format(result_dir, btn)
        btn += 1
        time.sleep(0.1)
        return_value, image = camera.read()
        res = driver.go(image)
        name = "{}.png".format(btn)

        draw_line(image)
        draw_res(image, res)

        cv2.imwrite(path, image)

        if (btn - flag) == 1200:
            break

    del(camera)
