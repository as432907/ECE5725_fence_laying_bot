import pygame
import pigame  # import pigame for touch support
import os
import sys
from pygame.locals import *
import time
import math
import RPi.GPIO as GPIO

''' 
--------------------------------------------------------------------
#   --- Setup GPIO - Motor------------------------------------------
--------------------------------------------------------------------
'''
# --- MODE --------------------------------------------------------
GPIO.setmode(GPIO.BCM)

# --- SETUP GPIO: Button ------------------------------------------
GPIOBtns = [17, 22, 23, 27]

for button in GPIOBtns:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- SETUP GPIO: MOTOR pins --------------------------------------
# DC Motor
AI_1_pin, AI_2_pin, PWM_Apin = 5, 6, 26
BI_1_pin, BI_2_pin, PWM_Bpin = 19, 13, 16
# Servo Motor
S_1_pin = 24

# Motor A
GPIO.setup(PWM_Apin, GPIO.OUT)
GPIO.setup(AI_1_pin, GPIO.OUT)
GPIO.setup(AI_2_pin, GPIO.OUT)
# Motor B
GPIO.setup(PWM_Bpin, GPIO.OUT)
GPIO.setup(BI_1_pin, GPIO.OUT)
GPIO.setup(BI_2_pin, GPIO.OUT)
# Servo Motor
GPIO.setup(S_1_pin, GPIO.OUT)

# PWM Setup
freq = 50
dc = 0
servo_val = 2.5

pwm_driver1 = GPIO.PWM(PWM_Apin, freq)
pwm_driver2 = GPIO.PWM(PWM_Bpin, freq)
servo_driver1 = GPIO.PWM(S_1_pin, freq)

pwm_driver1.start(dc)
pwm_driver2.start(dc)
servo_driver1.start(servo_val)
print("dc_clock", dc)

# --- SETUP GPIO: Comparator pins ---------------------------------
ENC_LEFT, ENC_RIGHT = 12, 20
GPIO.setup(ENC_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIOBtns_ctr = [0, 0, 0, 0]

# PID Constants
Kp, Kd, Ki = 25, 10, 5

'''--------------------------------------------------------------------
# --- Setup the display --------------------------------------------
--------------------------------------------------------------------'''
os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

# Colors
WHITE, BLACK, RED, GREEN = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0)

pygame.init()
pitft = pigame.PiTft()

screen_width, screen_height = 320, 240
m_screen = pygame.display.set_mode((320, 240))
m_screen.fill(WHITE)
pygame.mouse.set_visible(True)
pygame.display.update()

font_small = pygame.font.Font(None, 20)
font_mid = pygame.font.Font(None, 30)
font_big = pygame.font.Font(None, 50)

btn_start_rect = pygame.Rect(40, 180, 60, 40)
btn_quit_rect = pygame.Rect(240, 180, 60, 40)
btn_increase_rect = pygame.Rect(120, 180, 60, 40)
btn_decrease_rect = pygame.Rect(200, 180, 60, 40)

# Disk parameters
center = (screen_width // 2, screen_height // 2)
outer_radius = 90
hole_radius = 15
hole_offset = outer_radius - 20

'''--------------------------------------------------------------------
# --- FUNCTIONS - DEFINITIONS --------------------------------------------------
--------------------------------------------------------------------'''

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

def control_servo_1(angle):
    duty_cycle_map = {0: 2.5, 45: 4.6, 90: 6.7, 135: 8.8, 180: 10.9}
    servo_driver1.ChangeDutyCycle(duty_cycle_map.get(angle, 2.5))
    time.sleep(1)

def draw_disk(surface, angle):
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

def run_motor(disk_angle):
    prev_error, integral = 0, 0
    dc, dc_rev = 50, 25

    start_time = time.time()
    runtime, stop_time = 2, 1

    while True:
        error = 0
        if GPIO.input(ENC_LEFT) == GPIO.LOW:
            error = -1
        elif GPIO.input(ENC_RIGHT) == GPIO.LOW:
            error = 1
        elif GPIO.input(ENC_LEFT) == GPIO.HIGH and GPIO.input(ENC_RIGHT) == GPIO.HIGH:
            control_motor(dc, dc, "forward")
            continue
        elif GPIO.input(ENC_LEFT) == GPIO.LOW and GPIO.input(ENC_RIGHT) == GPIO.LOW:
            control_motor(dc_rev, dc_rev, "reverse")
            continue

        integral = max(min(integral + error, 100), -100)
        pid = Kp * error + Kd * (error - prev_error) + Ki * integral
        dc_A = max(0, min(100, 25 - pid))
        dc_B = max(0, min(100, 25 + pid))

        control_motor(dc_A, dc_B, "forward")
        prev_error = error

        if time.time() - start_time >= runtime:
            control_motor(0, 0, "forward")
            time.sleep(stop_time)

            disk_angle = (disk_angle + 45) % 180
            control_servo_1(disk_angle)

            start_time = time.time()

        time.sleep(0.1)

'''--------------------------------------------------------------------
# --- MAIN EVENT LOOP -------------------------------------------------
--------------------------------------------------------------------'''
code_running = True
start_time = time.time()
angle_controller = 0

while code_running:
    m_screen.fill(WHITE)

    pygame.draw.rect(m_screen, WHITE, btn_start_rect)
    m_screen.blit(font_small.render("START", True, BLACK), btn_start_rect)

    pygame.draw.rect(m_screen, WHITE, btn_quit_rect)
    m_screen.blit(font_small.render("QUIT", True, BLACK), btn_quit_rect)

    draw_disk(m_screen, angle_controller)

    pitft.update()
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if btn_start_rect.collidepoint(x, y):
                run_motor(angle_controller)
            elif btn_quit_rect.collidepoint(x, y):
                code_running = False

    if not GPIO.input(GPIOBtns[3]):
        code_running = False
        time.sleep(0.2)

    pygame.display.flip()

pwm_driver1.stop()
pwm_driver2.stop()
GPIO.cleanup()
pygame.quit()
del pitft
sys.exit()
