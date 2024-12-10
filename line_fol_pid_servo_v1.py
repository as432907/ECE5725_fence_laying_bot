import RPi.GPIO as GPIO
import time

# --- MODE --------------------------------------------------------
GPIO.setmode(GPIO.BCM)

# --- SETUP GPIO: Button ------------------------------------------
# Btn Array
Btn = [17, 22, 23, 27]

# GPIO setup for each button
for button in Btn:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set the comparator pin as input (to read the digital output)
ENC_LEFT = 12
ENC_RIGHT = 20

GPIO.setup(ENC_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- SETUP GPIO: MOTOR pins --------------------------------------
AI_1_pin = 5
AI_2_pin = 6
PWM_Apin = 26
BI_1_pin = 19
BI_2_pin = 13
PWM_Bpin = 16

GPIO.setup(PWM_Apin, GPIO.OUT)
GPIO.setup(AI_1_pin, GPIO.OUT)
GPIO.setup(AI_2_pin, GPIO.OUT)
GPIO.setup(PWM_Bpin, GPIO.OUT)
GPIO.setup(BI_1_pin, GPIO.OUT)
GPIO.setup(BI_2_pin, GPIO.OUT)

# ------------ Update PWM ---------------------
freq = 50
pwm_driver1 = GPIO.PWM(PWM_Apin, freq)
pwm_driver2 = GPIO.PWM(PWM_Bpin, freq)
pwm_driver1.start(0)
pwm_driver2.start(0)

# ------------ PID Constants -------------------
Kp = 25
Kd = 10
Ki = 5

# --------- Motor Control Function ---------------
def control_motor(dc_A, dc_B, direction):
    pwm_driver1.ChangeDutyCycle(dc_A)
    pwm_driver2.ChangeDutyCycle(dc_B)
    if direction == "forward":
        GPIO.output(AI_1_pin, GPIO.HIGH)
        GPIO.output(AI_2_pin, GPIO.LOW)
        GPIO.output(BI_1_pin, GPIO.HIGH)
        GPIO.output(BI_2_pin, GPIO.LOW)
    elif direction == "reverse":
        GPIO.output(AI_1_pin, GPIO.LOW)
        GPIO.output(AI_2_pin, GPIO.HIGH)
        GPIO.output(BI_1_pin, GPIO.LOW)
        GPIO.output(BI_2_pin, GPIO.HIGH)

# ----------- Run Motor Function ---------------------
def run_motor():
    prev_error = 0
    integral = 0
    dc = 50
    dc_rev = 25
    
    while True:
        error = 0
        # Check the state of each encoder
        if GPIO.input(ENC_LEFT) == GPIO.LOW:
            print("Black not detected on LEFT")
            error = -1
        elif GPIO.input(ENC_RIGHT) == GPIO.LOW:
            print("Black not detected on RIGHT")
            error = 1
        elif GPIO.input(ENC_LEFT) == GPIO.HIGH and GPIO.input(ENC_RIGHT) == GPIO.HIGH:
            print("Black line detected")
            control_motor(dc, dc, "forward")
            continue
        elif GPIO.input(ENC_LEFT) == GPIO.LOW and GPIO.input(ENC_RIGHT) == GPIO.LOW:
            print("Search for black line")
            control_motor(dc_rev, dc_rev, "reverse")
            continue

        # PID Controller
        integral = max(min(integral + error, 100), -100)
        pid = Kp * error + Kd * (error - prev_error) + Ki * integral
        dc_A = max(0, min(100, 25 - pid))
        dc_B = max(0, min(100, 25 + pid))
        
        control_motor(dc_A, dc_B, "forward")
        prev_error = error
        time.sleep(0.1) 

try:
    run_motor()

except KeyboardInterrupt:
    print("\nProgram interrupted by user")

# --- Reset all the GPIO pins by setting them to LOW --------------------
finally:
    pwm_driver1.stop()
    pwm_driver2.stop()
    GPIO.cleanup()