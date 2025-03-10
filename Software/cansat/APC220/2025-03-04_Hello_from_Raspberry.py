import serial
import time

ser = serial.Serial('/dev/serial0', 9600, timeout=1)  # Use ttyAMA0
ser.flush()

while True:
    ser.write(b"Hello from Raspberry Pi\n")
    time.sleep(1)
