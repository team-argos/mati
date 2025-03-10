import time
from gpiozero import PWMOutputDevice

# Define the buzzer pin (PWM0 is typically GPIO12)
buzzer = PWMOutputDevice(12)

# Define a function to play a tone
def play_tone(frequency, duration):
    """Play a tone on the buzzer."""
    if frequency == 0:  # Stop the buzzer
        buzzer.value = 0
    else:
        period = 1.0 / frequency
        buzzer.blink(on_time=period / 2, off_time=period / 2, n=None, background=True)
    time.sleep(duration)
    buzzer.off()

# Play some tones
try:
    play_tone(440, 1.0)  # A4 (440 Hz) for 1 second
    time.sleep(0.5)      # Pause for 0.5 seconds
    play_tone(880, 1.0)  # A5 (880 Hz) for 1 second
    time.sleep(0.5)      # Pause for 0.5 seconds
    play_tone(0, 1.0)    # Silence for 1 second
finally:
    buzzer.off()
