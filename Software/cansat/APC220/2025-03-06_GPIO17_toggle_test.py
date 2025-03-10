import RPi.GPIO as GPIO
import time

# Define the GPIO pin
SET_PIN = 17  

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SET_PIN, GPIO.OUT)

print("Toggling GPIO 17 (SET pin) every 2 seconds. Press Ctrl+C to stop.")

try:
    while True:
        GPIO.output(SET_PIN, GPIO.LOW)
        print("GPIO 17: LOW")
        time.sleep(2)

        GPIO.output(SET_PIN, GPIO.HIGH)
        print("GPIO 17: HIGH")
        time.sleep(2)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
