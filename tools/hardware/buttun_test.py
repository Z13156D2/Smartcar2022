from widgets_servo_test import Button
from widgets import Light
import time

up_but = Button(1, "UP")
down_but = Button(1, "DOWN")
left_but = Button(1, "LEFT")
right_but = Button(1, "RIGHT")

led = Light(2)


while True:
    if up_but.clicked():
        led.lightcontrol(2, 255, 0, 0)
        time.sleep(1)
        led.lightoff()
    if down_but.clicked():
        led.lightcontrol(2, 0, 255, 0)
        time.sleep(1)
        led.lightoff()
    if left_but.clicked():
        led.lightcontrol(3, 0, 0, 255)
        time.sleep(1)
        led.lightoff()
    if right_but.clicked():
        led.lightcontrol(4, 0, 255, 0)
        time.sleep(1)
        led.lightoff()






