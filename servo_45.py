import RPi.GPIO as GPIO
import time

# Setup
servo_pin = 24  # Replace with your GPIO pin number
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# Start PWM
pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz PWM frequency
pwm.start(0)

def set_angle(angle):
    """Set the servo to the specified angle (0-180 degrees)."""
    duty = 2 + (angle / 18)  # Map 0° -> 2%, 180° -> 12%
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Allow the servo to reach the position
    pwm.ChangeDutyCycle(0)  # Turn off the pulse to stop jittering

try:
    for angle in range(0, 181, 45):  # 0°, 45°, 90°, 135°, 180°
        print(f"Moving to {angle}°")
        set_angle(angle)
        time.sleep(1)  # Pause for 1 second

finally:
    pwm.stop()
    GPIO.cleanup()
    print("Cleanup and exit.")
