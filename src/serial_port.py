#!/usr/bin/python
# -*- coding: utf-8 -*-
import serial
import time
import config
import sys

sys.path.append("../")
from threading import Lock

class Serial:
	def __init__(self):
		portx = "/dev/ttyUSB0"
		if config.CONTROLLER == "wobot":
			bps = 115200
		elif config.CONTROLLER == "mc601":
			bps = 380400
		else:
			bps = 115200

		self.res = None
		self.serial = serial.Serial(portx, int(bps), timeout=0.004, parity=serial.PARITY_NONE, stopbits=1)
		time.sleep(1)

	def write(self, data):
		self.res = ''
		self.serial.reset_input_buffer()
		lock = Lock()
		lock.acquire()
		try:
			self.serial.write(data)
			self.serial.flush()
			self.res = self.serial.readline()
			for i in range(10):
				if(self.res[-2:] == b'\r\n'):
					break
				else:
					self.res = self.res + self.serial.readline()
			self.serial.flush()

		except ZeroDivisionError as e:
			print('except:', e)
		finally:
			lock.release()
			pass

	def read(self):
		return self.res

serial_connection = Serial()
