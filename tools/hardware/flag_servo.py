from widgets_servo_test import Servo
import time
flag_servo = Servo(2)
time.sleep(1)
#flag_servo.servocontrol(-45, 60)  #左
#time.sleep(2)

flag_servo.servocontrol(121, 60)  #左
time.sleep(2)
flag_servo.servocontrol(38, 60)
time.sleep(2)
flag_servo.servocontrol(-45, 60)  #右
time.sleep(2)
flag_servo.servocontrol(40, 60)
time.sleep(2)
flag_servo.servocontrol(-128, 60)  #中
time.sleep(2)
flag_servo.servocontrol(40, 60)
time.sleep(2)