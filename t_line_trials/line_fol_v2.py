import RPi.GPIO as GPIO
import time

# ----Define GPIO pins for sensors--------------------------------
sensor_pins = [11, 12, 15] 

GPIO.setmode(GPIO.BCM)

for pin in sensor_pins:
    GPIO.setup(pin, GPIO.IN, pull_up=True)

# --- SETUP GPIO: MOTOR pins --------------------------------------

AI_1_pin = 5
AI_2_pin = 6
PWM_Apin = 26
BI_1_pin = 19
BI_2_pin = 13
PWM_Bpin = 16

GPIO.setup(PWM_Apin, GPIO.OUT) # Connected to PWMA
GPIO.setup(AI_1_pin, GPIO.OUT) # Connected to AIN1
GPIO.setup(AI_2_pin, GPIO.OUT) # Connected to AIN2

GPIO.setup(PWM_Bpin, GPIO.OUT) # Connected to PWMB
GPIO.setup(BI_1_pin, GPIO.OUT) # Connected to BIN1
GPIO.setup(BI_2_pin, GPIO.OUT) # Connected to BIN2

freq = 50
dc = 0

## ------------ Update PWM ---------------------
pwm_driver1 = GPIO.PWM(PWM_Apin, freq) 
pwm_driver1.start(dc)
pwm_driver2 = GPIO.PWM(PWM_Bpin, freq) 
pwm_driver2.start(dc)
print("dc_clock", dc)

# Main loop
code_running =  True
while code_running:
    if sensor_values[0] == 0:
        dc = 100
		pwm_driver1.ChangeDutyCycle(dc)
		print("dc_clock", dc)
		GPIO.output(AI_1_pin, GPIO.HIGH) # Set AIN1
		GPIO.output(AI_2_pin, GPIO.LOW) # Set AIN2
		ctr_btn[0]+=1
		time.sleep(1)
    
    else
        dc = 0
		pwm_driver1.ChangeDutyCycle(dc)
		print("dc_clock", dc)
		pwm_driver1.ChangeDutyCycle(dc)
		pwm_driver2.ChangeDutyCycle(dc)
		print("dc_clock", dc)
		time.sleep(1)
        code_running = False

# --- Reset all the GPIO pins by setting them to LOW --------------------
pwm_driver1.stop()
pwm_driver2.stop()
GPIO.cleanup()