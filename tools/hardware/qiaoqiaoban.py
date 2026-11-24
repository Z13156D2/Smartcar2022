from driver import Driver
from cart import Cart
import time

driver = Driver()
cart = Cart()

driver.cart.move([40, -40, 40, -40])
time.sleep(50)