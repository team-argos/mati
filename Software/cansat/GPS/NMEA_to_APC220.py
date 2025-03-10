import pigpio
import serial
import time
import pynmea2  # You'll need to install this: pip install pynmea2

# Define GPIO pins
RX_PIN = 5  # GPIO5 (connected to TX of GPS)
BAUD_RATE = 9600

# Initialize pigpio and configure software serial
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpio daemon")
    exit()

pi.bb_serial_read_open(RX_PIN, BAUD_RATE)
radio = serial.Serial('/dev/serial0', 9600, timeout=1)

def extract_gps_data(nmea_sentence):
    """Extract time, latitude, longitude, and altitude from NMEA sentence"""
    try:
        msg = pynmea2.parse(nmea_sentence)
        
        # Check if it's a GGA message (contains altitude)
        if isinstance(msg, pynmea2.GGA):
            time_str = msg.timestamp.strftime("%H:%M:%S") if msg.timestamp else "No time"
            lat = msg.latitude if msg.latitude else 0.0
            lon = msg.longitude if msg.longitude else 0.0
            alt = msg.altitude if msg.altitude else 0.0
            
            # Format data as a simple string
            data_str = f"T:{time_str},LAT:{lat:.6f},LON:{lon:.6f},ALT:{alt:.1f}"
            return data_str
            
    except pynmea2.ParseError:
        pass
    except AttributeError:
        pass
        
    return None

accumulated_data = ""

try:
    print("GPS Data Transmitter Running...")
    print("Sending only time, latitude, longitude, and altitude via radio")
    print("Press Ctrl+C to exit")
    
    while True:
        (count, data) = pi.bb_serial_read(RX_PIN)
        if count:
            # Decode the data
            text = data.decode('utf-8', errors='ignore')
            accumulated_data += text
            
            # Process complete NMEA sentences
            lines = accumulated_data.split('\r\n')
            if len(lines) > 1:
                # Keep the last incomplete line
                accumulated_data = lines[-1]
                
                # Process all complete lines
                for line in lines[:-1]:
                    if line.startswith('$'):
                        extracted_data = extract_gps_data(line)
                        if extracted_data:
                            print(f"Sending: {extracted_data}")
                            # Send the extracted data over radio
                            radio.write(f"{extracted_data}\r\n".encode())
                            
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    print("Closing connections...")
    pi.bb_serial_read_close(RX_PIN)
    pi.stop()
    radio.close()
    print("Done.")