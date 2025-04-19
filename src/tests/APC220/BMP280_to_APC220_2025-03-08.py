import time
import board
import adafruit_bmp280
import serial
from datetime import datetime

# Initialize I2C and BMP280 sensor
i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
bmp280.sea_level_pressure = 1013.25

# Initialize APC220 radio on serial port
# Change '/dev/serial0' to the appropriate port if different
radio = serial.Serial('/dev/serial0', 9600, timeout=1)

try:
    print("BMP280 Sensor to APC220 Radio Transmitter")
    print("Press Ctrl+C to exit")
    
    while True:
        # Get current timestamp
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Read sensor data
        temperature = bmp280.temperature
        pressure = bmp280.pressure
        altitude = bmp280.altitude
        
        # Format data string
        data_string = f"T:{current_time},TEMP:{temperature:.1f},PRES:{pressure:.1f},ALT:{altitude:.2f}"
        
        # Print to console
        print(data_string)
        
        # Send over APC220 radio
        radio.write(f"{data_string}\r\n".encode())
        
        # Wait for 2 seconds before next reading
        time.sleep(2)

except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Clean up
    if 'radio' in locals():
        radio.close()
    print("Done.")