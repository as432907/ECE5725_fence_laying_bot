"""
### ----------- Import Libraries here ----------------------------
"""

import time
import RPi.GPIO as GPIO


"""
### ------------ SETUP --------------------------------------------
"""
# --- MODE --------------------------------------------------------
GPIO.setmode(GPIO.BCM)

# --- SETUP GPIO: MOTOR pins --------------------------------------

S1_pin = 26
GPIO.setup(S1_pin, GPIO.OUT)

freq = 50
dc = 0

## ------------ Update PWM ---------------------
servo_driver1 = GPIO.PWM(S1_pin, freq) 

servo_driver1.start(dc)
print("Waiting time for 2sec")
time.sleep(1)

## ------------ Moving servo ---------------------
print("Rotating servo in 180 degress in 5 steps")
# code_running = True
while dc < 12:
    dc = dc + 1
    servo_driver1.ChangeDutyCycle(dc)
    time.sleep(1)

# except KeyboardInterrupt:
#     print("\nProgram interrupted by user")

# --- Reset all the GPIO pins by setting them to LOW --------------------
# finally:
servo_driver1.stop()
GPIO.cleanup()
