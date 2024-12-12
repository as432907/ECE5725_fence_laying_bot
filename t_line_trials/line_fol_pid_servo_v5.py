

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
# mode = GPIO.getmode()
# print('mode:', mode)


# --- SETUP GPIO: Button ------------------------------------------

# Btn Array
Btn = [17, 22, 23, 27]

# GPIO setup for each button
for button in Btn:
	GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set the comparator pin as input (to read the digital output)
ENC_CENTER = 23 # center line follower
ENC_LEFT = 12 # left line follower
ENC_RIGHT = 20 # right line follower

GPIO.setup(ENC_CENTER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
dc_0 = 0
dc = 50
dc_rev = 50
# ------------ Update PWM ---------------------
pwm_driver1 = GPIO.PWM(PWM_Apin, freq) 
pwm_driver1.start(dc_0)
pwm_driver2 = GPIO.PWM(PWM_Bpin, freq) 
pwm_driver2.start(dc_0)
print("dc_clock", dc_0)

# ------------ PID -------------------------------------------
Kp = 10
Kd = 2
Ki = 1

prev_error = 0
integral = 0
# -------------------- Motor Driver -------------

motor_running = True

while motor_running:
    # Check the state of each button
    if GPIO.input(ENC_CENTER) == GPIO.HIGH and GPIO.input(ENC_RIGHT) == GPIO.LOW and GPIO.input(ENC_LEFT) == GPIO.LOW:
        print("Black line detected")
        error = 0
        pwm_driver1.ChangeDutyCycle(dc)
        pwm_driver2.ChangeDutyCycle(dc)
        print("dc_clock", dc)
        GPIO.output(AI_1_pin, GPIO.HIGH) # Set AIN1
        GPIO.output(AI_2_pin, GPIO.LOW) # Set AIN2
        GPIO.output(BI_1_pin, GPIO.HIGH) # Set BIN1
        GPIO.output(BI_2_pin, GPIO.LOW) # Set BIN2
        time.sleep(0.2)
        prev_error = error
        
    elif GPIO.input(ENC_CENTER) == GPIO.LOW and GPIO.input(ENC_LEFT) == GPIO.HIGH and GPIO.input(ENC_RIGHT) == GPIO.LOW: 
        print("moving in RIGHT")
        error = -1
        integral = max(min(integral + error, 100), -100)
        pid = Kp * error + Kd * (error - prev_error) + Ki * integral
        dc_A = max(0, min(100, 25 + pid))
        dc_B = max(0, min(100, 25 - pid))
        pwm_driver1.ChangeDutyCycle(dc_A)
        pwm_driver2.ChangeDutyCycle(dc_B)
        # print("dc_clock", dc)
        GPIO.output(AI_1_pin, GPIO.HIGH) # Set AIN1
        GPIO.output(AI_2_pin, GPIO.LOW) # Set AIN2
        GPIO.output(BI_1_pin, GPIO.HIGH) # Set BIN1
        GPIO.output(BI_2_pin, GPIO.LOW) # Set BIN2
        time.sleep(0.2)
        prev_error = error

    elif GPIO.input(ENC_CENTER) == GPIO.LOW and GPIO.input(ENC_RIGHT) == GPIO.HIGH and GPIO.input(ENC_LEFT) == GPIO.LOW:
        print("moving in LEFT")
        error = 1
        integral = max(min(integral + error, 100), -100)
        pid = Kp * error + Kd * (error - prev_error) + Ki * integral
        dc_A = max(0, min(100, 25 + pid))
        dc_B = max(0, min(100, 25 - pid))
        pwm_driver1.ChangeDutyCycle(dc_A)
        pwm_driver2.ChangeDutyCycle(dc_B)
        # print("dc_clock", dc)
        GPIO.output(AI_1_pin, GPIO.HIGH) # Set AIN1
        GPIO.output(AI_2_pin, GPIO.LOW) # Set AIN2
        GPIO.output(BI_1_pin, GPIO.HIGH) # Set BIN1
        GPIO.output(BI_2_pin, GPIO.LOW) # Set BIN2
        time.sleep(0.2)
        prev_error = error

    elif GPIO.input(ENC_CENTER) == GPIO.LOW and GPIO.input(ENC_RIGHT) == GPIO.LOW and GPIO.input(ENC_LEFT) == GPIO.LOW:
        print("move back")
        error = 0
        pwm_driver1.ChangeDutyCycle(dc)
        pwm_driver2.ChangeDutyCycle(dc)
        print("dc_clock", dc)
        GPIO.output(AI_1_pin, GPIO.LOW) # Set AIN1
        GPIO.output(AI_2_pin, GPIO.HIGH) # Set AIN2
        GPIO.output(BI_1_pin, GPIO.LOW) # Set BIN1
        GPIO.output(BI_2_pin, GPIO.HIGH) # Set BIN2
        time.sleep(0.2)
        prev_error = error

# except KeyboardInterrupt:
#     print("\nProgram interrupted by user")


# # --- Reset all the GPIO pins by setting them to LOW --------------------
# finally:
pwm_driver1.stop()
pwm_driver2.stop()
GPIO.cleanup()
