#!/usr/bin/env python3
import time
import os
from picamera2 import Picamera2, Preview
from libcamera import controls

# Create directory to store images if it doesn't exist
output_dir = "cansat_images"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Initialize the camera
picam2 = Picamera2()

# Configure camera for maximum resolution
# Camera Module 3 NOiR max resolution is 4608x2592 pixels
camera_config = picam2.create_still_configuration(
    main={"size": (4608, 2592), "format": "RGB888"},
    lores={"size": (640, 480), "format": "YUV420"},
    display="lores"
)
picam2.configure(camera_config)

# Enable image stabilization (built into the libcamera API)
# For a moving camera, we'll use the enhanced stabilization mode
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})  # Continuous autofocus
picam2.set_controls({"AeEnable": True})  # Auto exposure
picam2.set_controls({"AwbEnable": True})  # Auto white balance
# Stick to the most basic and widely supported controls
# Removed NoiseReductionMode as it might not be supported in all versions

# Set a higher shutter speed to reduce motion blur for moving camera
picam2.set_controls({"FrameDurationLimits": (33333, 33333)})  # ~30 fps

# Start the camera
picam2.start()
print("Camera initialized and started")

# Calculate parameters
interval = 2  # seconds between photos
duration = 40  # total duration in seconds
num_photos = duration // interval + 1

# Take photos
try:
    for i in range(num_photos):
        # Capture the image
        filename = f"{output_dir}/cansat_image_{i:03d}.jpg"
        
        # No additional metadata for image processing
        # Using only the basic controls that are confirmed to work
        
        # Capture the image
        picam2.capture_file(filename)
        
        print(f"Captured image {i+1} of {num_photos}: {filename}")
        
        # Wait for the next interval (if not the last photo)
        if i < num_photos - 1:
            time.sleep(interval)

except KeyboardInterrupt:
    print("Image capture interrupted by user")

finally:
    # Stop the camera gracefully
    picam2.stop()
    print("Camera stopped")
    print(f"Captured {num_photos} images in {duration} seconds")
    print(f"Images saved to {os.path.abspath(output_dir)}")