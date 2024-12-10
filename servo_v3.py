import time
import RPi.GPIO as GPIO

# --- MODE --------------------------------------------------------
GPIO.setmode(GPIO.BCM)


# --- SETUP GPIO: MOTOR pins --------------------------------------
S1_pin = 24
GPIO.setup(S1_pin, GPIO.OUT)

freq = 50  
dc = 2.5    

# Initialize PWM on the pin
servo_driver1 = GPIO.PWM(S1_pin, freq)
servo_driver1.start(dc)  
print("Waiting time for 1 second...")
time.sleep(1) 

# ------------ Moving servo ---------------------
# Rotating servo from 0° to 180° in 45-degree increments
print("Rotating servo in 45-degree steps from 0 to 180 degrees:")
for dc_angle in [2.5, 5, 7.5, 10, 12.5]:  # Duty cycles for 0°, 45°, 90°, 135°, 180°
    servo_driver1.ChangeDutyCycle(dc_angle)  
    time.sleep(1) 

# Now move the servo back to 0° (reset position)
print("Returning to 0 degrees:")
servo_driver1.ChangeDutyCycle(2.5)  
time.sleep(1)

# --- Cleanup GPIO -----------------------------------------
servo_driver1.stop()  
GPIO.cleanup()