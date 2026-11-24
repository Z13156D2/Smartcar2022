from widgets_servo_test import Light, Button, Buzzer
# from widgets import
import time

led = Light(1)
buz = Buzzer()
but1 = Button(1, "1")
but2 = Button(1, "2")
but3 = Button(1, "3")
but4 = Button(1, "4")

led.lightoff()

for i in range(125566):
    print(i)
    #led.lightoff()
    # if but1.clicked():
    #     buz.rings()
    #     led.lightcontrol(0, 255, 0, 0)
    #     # led.lightcontrol(2, 255, 0, 0)
    #     # led.lightcontrol(3, 255, 0, 0)
    #     # led.lightcontrol(4, 255, 0, 0)
    #     time.sleep(1)
    #     led.lightoff()
    # if but2.clicked():
    #     buz.rings()
    #     led.lightcontrol(0, 0, 255, 0)
    #     # led.lightcontrol(2, 0, 255, 0)
    #     # led.lightcontrol(3, 0, 255, 0)
    #     # led.lightcontrol(4, 0, 255, 0)
    #     time.sleep(1)
    #     led.lightoff()
    # if but3.clicked():
    #     buz.rings()
    #     led.lightcontrol(0, 0, 0, 255)
    #     # led.lightcontrol(2, 0, 0, 255)
    #     # led.lightcontrol(3, 0, 0, 255)
    #     # led.lightcontrol(4, 0, 0, 255)
    #     time.sleep(1)
    #     led.lightoff()
    # if but4.clicked():
    #     buz.rings()
    #     led.lightcontrol(0, 255, 255, 255)
    #     # led.lightcontrol(2, 255, 255, 255)
    #     # led.lightcontrol(3, 255, 255, 255)
    #     # led.lightcontrol(4, 255, 255, 255)
    #     time.sleep(1)
    #     led.lightoff()
    # led.lightoff()

    for i in range(3):
        led.lightcontrol(0, 255, 0, 0)
        time.sleep(0.1)
        led.lightoff()
        time.sleep(0.1)

    for i in range(3):
        led.lightcontrol(0, 0, 255, 0)
        time.sleep(0.1)
        led.lightoff()
        time.sleep(0.1)

    # led.lightcontrol(1, 255, 255, 255)
    # time.sleep(0.5)
    # led.lightoff()
    # time.sleep(0.5)
    # led.lightcontrol(2, 255, 0, 0)
    # time.sleep(0.5)
    # led.lightoff()
    # time.sleep(0.5)
    # led.lightcontrol(3, 0, 0, 255)
    # time.sleep(0.5)
    # led.lightoff()
    # time.sleep(0.5)
    # led.lightcontrol(4, 0, 255, 255)
    # time.sleep(0.5)
    # led.lightoff()
    # time.sleep(0.5)



