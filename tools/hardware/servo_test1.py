# uartdemo.py
from serial import Serial

try:
	uartport = "/dev/ttyPS0"
	bps = 9600
	timeout = 5

	serial = Serial(uartport,bps,timeout=timeout)

	result = serial.write("HelloWorld".encode())
	print(result)

	serial.close()

except Exception as e:
	print("----error-----",e)