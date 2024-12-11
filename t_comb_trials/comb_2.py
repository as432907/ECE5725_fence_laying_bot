import pygame
import pigame  # import pigame for touch support
import os
import sys
from pygame.locals import *
import time
import math

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
# # Servo Motor 
S_1_pin = 24

# MOTOR A
GPIO.setup(PWM_Apin, GPIO.OUT)  # Connected to PWMA
GPIO.setup(AI_1_pin, GPIO.OUT)  # Connected to AIN1
GPIO.setup(AI_2_pin, GPIO.OUT)  # Connected to AIN2
# MOTOR B
GPIO.setup(PWM_Bpin, GPIO.OUT)  # Connected to PWMB
GPIO.setup(BI_1_pin, GPIO.OUT)  # Connected to BIN1
GPIO.setup(BI_2_pin, GPIO.OUT)  # Connected to BIN2
# SERVO MOTOR
GPIO.setup(S_1_pin, GPIO.OUT)

# # Initial Setup
freq = 50
dc = 0
servo_val = 2.5

# ------------ Update PWM ---------------------
pwm_driver1 = GPIO.PWM(PWM_Apin, freq)
pwm_driver2 = GPIO.PWM(PWM_Bpin, freq)
servo_driver1 = GPIO.PWM(S_1_pin, freq)

pwm_driver1.start(dc)
pwm_driver2.start(dc)
servo_driver1.start(servo_val)
print("dc_clock", dc)

# --- SETUP GPIO: Comparator pins --------------------------------------

ENC_LEFT = 12
ENC_RIGHT = 20

GPIO.setup(ENC_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ------- COUNTER ------------------------
GPIOBtns_ctr = [0, 0, 0, 0]

# ------------ PID Constants -------------------
Kp = 25
Kd = 10
Ki = 5

'''
--------------------------------------------------------------------
# --- Setup the display --------------------------------------------
--------------------------------------------------------------------
'''
# Setup environment for the framebuffer (required when using pigame)
os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

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
def control_servo_1(angle):
    print("Rotating servo in 45-degree steps from 0 to 180 degrees:")
    servo_driver1.ChangeDutyCycle(angle)
    time.sleep(1)

# -----------Draw Disk --------------------
def draw_disk(surface, angle):
    """Draws the disk and updates the position of the small circles."""
    pygame.draw.circle(surface, BLACK, center, outer_radius + 10, 2)
    pygame.draw.circle(surface, BLACK, center, outer_radius, 2)

    for i in range(7):
        theta = math.radians(270 - i * 45 + angle)
        line_x = center[0] + hole_offset * math.cos(theta)
        line_y = center[1] - hole_offset * math.sin(theta)
        pygame.draw.line(surface, BLACK, center, (int(line_x), int(line_y)), 2)

        hole_x = center[0] + hole_offset * math.cos(theta)
        hole_y = center[1] - hole_offset * math.sin(theta)
        pygame.draw.circle(surface, WHITE, (int(hole_x), int(hole_y)), hole_radius)
        pygame.draw.circle(surface, BLACK, (int(hole_x), int(hole_y)), hole_radius, 2)

        hole_number_text = font_small.render(str(i + 1), True, BLACK)
        hole_text_rect = hole_number_text.get_rect(center=(int(hole_x), int(hole_y)))
        surface.blit(hole_number_text, hole_text_rect)

# -----------Run Motor --------------------
def run_motor(disk_angle):
    prev_error = 0
    integral = 0
    dc = 50
    dc_rev = 25

    start_time = time.time()
    runtime = 2
    stop_time = 1

    while True:
        error = 0
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
            print("Searching for black line")
            control_motor(dc_rev, dc_rev, "reverse")
            continue

        integral = max(min(integral + error, 100), -100)
        pid = Kp * error + Kd * (error - prev_error) + Ki * integral
        dc_A = max(0, min(100, 25 - pid))
        dc_B = max(0, min(100, 25 + pid))

        control_motor(dc_A, dc_B, "forward")
        prev_error = error

        running_time = time.time() - start_time

        if running_time >= runtime:
            print(f"Running for {runtime} seconds. Stopping for {stop_time} seconds.")
            control_motor(0, 0, "forward")
            time.sleep(stop_time)

            disk_angle += 45
            if disk_angle >= 180:
                disk_angle = 0

            control_servo_1(disk_angle)
            start_time = time.time()

        time.sleep(0.1)

'''
# --- MAIN VARIABLES --------------------------------------------------
'''
code_running = True
start_time = time.time()
angle_controller = 0

'''
# --- MAIN EVENT LOOP -------------------------------------------------
'''

while code_running:
    current_time = time.time() - start_time

    m_screen.fill(WHITE)

    pygame.draw.rect(m_screen, btn_start_color, btn_start_rect)
    btn_start_surface = font_small.render(btn_start_text, True, btn_start_text_color)
    btn_start_text_rect = btn_start_surface.get_rect(center=btn_start_rect.center)
    m_screen.blit(btn_start_surface, btn_start_text_rect)

    pygame.draw.rect(m_screen, btn_quit_color, btn_quit_rect)
    btn_quit_surface = font_small.render(btn_quit_text, True, btn_quit_text_color)
    btn_quit_text_rect = btn_quit_surface.get_rect(center=btn_quit_rect.center)
    m_screen.blit(btn_quit_surface, btn_quit_text_rect)
    draw_disk(m_screen, angle_controller)

    pitft.update()
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            print(f"Mouse down at ({x}, {y})")
        elif event.type == MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            print(f"Mouse down at ({x}, {y})")
            if btn_start_rect.collidepoint(x, y):
                print("Start button pressed")
                run_motor(angle_controller)
            if btn_quit_rect.collidepoint(x, y):
                print("Quit button pressed")
                code_running = False

    if not GPIO.input(GPIOBtns[3]):
        print("Quitting Program")
        code_running = False
        time.sleep(0.2)

    pygame.display.flip()

pwm_driver1.stop()
pwm_driver2.stop()
GPIO.cleanup()

pygame.quit()
del pitft
sys.exit()
