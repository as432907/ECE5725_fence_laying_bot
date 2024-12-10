import pygame
import pigame  # import pigame for touch support
import os
import sys
from pygame.locals import *
import time
import math

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Setup environment for the framebuffer (required when using pigame)
os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

''' 
--------------------------------------------------------------------
#   --- Setup GPIO - Motor------------------------------------------
--------------------------------------------------------------------
'''
import RPi.GPIO as GPIO

# --- MODE --------------------------------------------------------
GPIO.setmode(GPIO.BCM)

# --- SETUP GPIO: Button ------------------------------------------
GPIOBtns = [17, 22, 23, 27]

# GPIO setup for each button
for button in GPIOBtns:
	GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# --- SETUP GPIO: MOTOR pins --------------------------------------
# # DC MOTOR 
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

# # SERVO MOTOR
S1_pin = 24
GPIO.setup(S1_pin, GPIO.OUT)

# # Initial Setup
freq = 50
dc = 0
servo_val = 2.5

# --- SETUP GPIO: Comparator pins --------------------------------------

ENC_LEFT = 12
ENC_RIGHT = 20

GPIO.setup(ENC_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

## ------------ Update PWM ---------------------
pwm_driver1 = GPIO.PWM(PWM_Apin, freq) 
pwm_driver2 = GPIO.PWM(PWM_Bpin, freq) 
servo_driver1 = GPIO.PWM(S1_pin, freq)

pwm_driver1.start(dc)
pwm_driver2.start(dc)
servo_driver1.start(servo_val) 
print("dc_clock", dc)

## ------- COUNTER ------------------------
GPIOBtns_ctr = [0,0,0,0]

## ------------ PID Constants -------------------
Kp = 25
Kd = 10
Ki = 5

'''
--------------------------------------------------------------------
# --- Setup the display --------------------------------------------
--------------------------------------------------------------------
'''
# Initialize pygame and pigame for touchscreen support
pygame.init()
pitft = pigame.PiTft()

screen_width = 320
screen_height = 240
m_screen = pygame.display.set_mode((320, 240))
m_screen.fill(WHITE)
pygame.mouse.set_visible(True)
pygame.display.update()

# Font setup
font_small = pygame.font.Font(None, 20)
font_mid = pygame.font.Font(None, 30)
font_big = pygame.font.Font(None, 50)

# Start button setup
btn_start_text = 'START'
btn_start_text_color = BLACK
btn_start_color = WHITE
btn_start_rect = pygame.Rect(40, 180, 60, 40)

# Quit button setup
btn_quit_text = 'QUIT'
btn_quit_text_color = BLACK
btn_quit_color = WHITE
btn_quit_rect = pygame.Rect(240, 180, 60, 40)

# Disk parameters
center = (screen_width // 2, screen_height // 2)
outer_radius = 90
hole_radius = 15
hole_offset = outer_radius - 20
angle = 0  # Example angle for rotation    

# Left History Setup
history_text_color = BLACK
left_history = ['Left History', 'Stop 0', 'Stop 0', 'Stop 0']
right_history = ['Right History', 'Stop 0', 'Stop 0', 'Stop 0']

'''
# --- FUNCTIONS - DEFINITIONS --------------------------------------------------
'''

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

# -----------Servo Control Function --------------------
def control_servo(dc_angle):
    print("Rotating servo in 45-degree steps from 0 to 180 degrees:")
    servo_driver1.ChangeDutyCycle(dc_angle)  
    time.sleep(1)
# ----------- Run Motor Function ---------------------
def run_motor():
    prev_error = 0
    integral = 0
    dc = 50
    dc_rev = 25

    # Track runtime and stop time
    start_time = time.time()  # Record the start time of the current cycle
    runtime = 2  # Run for 5 seconds
    stop_time = 1  # Stop for 1 seconds
    running_time = 0  # Variable to track how long the motor has been running in the cycle
    dc_angle = 2.5  # Initial servo angle (0 degrees)
    
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

        # Calculate how long the motor has been running
        running_time = time.time() - start_time

        if running_time >= runtime:
            print(f"Running for {runtime} seconds. Stopping for {stop_time} seconds.")
            # Stop the motor for 2 seconds
            control_motor(0, 0, "forward")  # Set PWM duty cycle to 0 to stop the motors
            time.sleep(stop_time)  # Stop for 1 seconds

            dc_angle += 2.25 # Update the dc_angle for next stop
            # Run the servo during the stop period
            control_servo(dc_angle)
            
            # If the servo exceeds 180 degrees (12.5% duty cycle), reset to 0 degrees (2.5% duty cycle)
            if dc_angle > 12.5:
                dc_angle = 2.5

            start_time = time.time()  # Reset the start time for the next cycle

        time.sleep(0.1)  

# Function to render history list
def render_history_list(screen, font, text_list, start_pos, color):
    x, y = start_pos
    for text in text_list:
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))
        y += 20  # Increment y to avoid overlap

# Function to update history
def update_history(history, new_entry):
    history.pop(1)  # Remove the oldest entry
    history.append(new_entry)  # Add the new entry

def draw_disk():
    """
    Draws a rotating disk with a boundary circle, 7 lines to holes, 7 holes at 45-degree intervals,
    and labels each hole.
    """
    # Draw the outer boundary circle
    pygame.draw.circle(m_screen, (0, 0, 0), center, outer_radius + 10, 2)  # Slightly larger boundary
    pygame.draw.circle(m_screen, (0, 0, 0), center, outer_radius, 2)

    # Draw 7 lines and holes at 45-degree intervals (clockwise rotation)
    for i in range(7):  # Only 7 lines and holes
        theta = math.radians(-i * 45 + angle)  # Negative angle for clockwise rotation
        line_x = center[0] + hole_offset * math.cos(theta)  # End point of the line (to the hole)
        line_y = center[1] - hole_offset * math.sin(theta)  # Same offset for holes

        # Draw the line from the center to the hole position
        pygame.draw.line(m_screen, (0, 0, 0), center, (int(line_x), int(line_y)), 2)

        # Draw the hole at the same position
        hole_x = center[0] + hole_offset * math.cos(theta)
        hole_y = center[1] - hole_offset * math.sin(theta)
        pygame.draw.circle(m_screen, (255, 255, 255), (int(hole_x), int(hole_y)), hole_radius)
        pygame.draw.circle(m_screen, (0, 0, 0), (int(hole_x), int(hole_y)), hole_radius, 2)  # Hole border

        # Label each hole with a number (1 to 7)
        hole_number_text = font_small.render(str(i + 1), True, (0, 0, 0))
        hole_text_rect = hole_number_text.get_rect(center=(int(hole_x), int(hole_y)))
        m_screen.blit(hole_number_text, hole_text_rect)

'''
# --- MAIN VARIABLES --------------------------------------------------
'''
code_running = True
start_time = time.time()

'''
# --- MAIN EVENT LOOP -------------------------------------------------
'''

while code_running:
    # print("Entered here")
    current_time = time.time() - start_time

    m_screen.fill(WHITE)

    # Draw the start button
    pygame.draw.rect(m_screen, btn_start_color, btn_start_rect)
    btn_start_surface = font_small.render(btn_start_text, True, btn_start_text_color)
    btn_start_text_rect = btn_start_surface.get_rect(center=btn_start_rect.center)
    m_screen.blit(btn_start_surface, btn_start_text_rect)

    # Draw the quit button
    pygame.draw.rect(m_screen, btn_quit_color, btn_quit_rect)
    btn_quit_surface = font_small.render(btn_quit_text, True, btn_quit_text_color)
    btn_quit_text_rect = btn_quit_surface.get_rect(center=btn_quit_rect.center)
    m_screen.blit(btn_quit_surface, btn_quit_text_rect)
    
    draw_disk()
    # Draw Left & Right History
    # render_history_list(m_screen, font_small, left_history, (40, 80), history_text_color)
    # render_history_list(m_screen, font_small, right_history, (220, 80), history_text_color)
    pitft.update()
    # Event handling
    for event in pygame.event.get():
        if (event.type is MOUSEBUTTONUP):
            x, y = pygame.mouse.get_pos()
            print(f"Mouse down at ({x}, {y})")
        elif (event.type is MOUSEBUTTONDOWN):
            x, y = pygame.mouse.get_pos()
            print(f"Mouse down at ({x}, {y})")
            # START motor Button
            if btn_start_rect.collidepoint(x, y):
                print("Start button pressed")
                run_motor()
            # QUIT Screen Button
            if btn_quit_rect.collidepoint(x, y):
                print("Quit button pressed")
                code_running = False

    if not GPIO.input(GPIOBtns[3]):
        print("Quitting Program")
        code_running = False   
        time.sleep(0.2)

    # Update the display
    pygame.display.flip()

# --- Reset all the GPIO pins by setting them to LOW --------------------
pwm_driver1.stop()
pwm_driver2.stop()
GPIO.cleanup()

# Quit Pygame and cleanup
pygame.quit()
del pitft
sys.exit()


# --- Reset all the GPIO pins by setting them to LOW --------------------
pwm_driver1.stop()
pwm_driver2.stop()
GPIO.cleanup()

# Quit Pygame and cleanup
pygame.quit()
del pitft
sys.exit()
