import time
import RPi.GPIO as GPIO
import pygame
import pigame
import math
import sys
import os
from pygame.locals import *

# Setup environment for the framebuffer (required when using pigame)
os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)

# --- SETUP GPIO: Button ------------------------------------------
GPIOBtns = [17, 22, 23, 27]
servo_pin = 24

# GPIO setup for each button
for button in GPIOBtns:
	GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(servo_pin, GPIO.OUT)

freq = 50
dc = 2.5
servo_dc = [2.5, 4.6, 6.7, 8.8, 10.9]
servo_driver1 = GPIO.PWM(servo_pin, freq)

# --- Pygame Setup ---

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

pygame.init()
pitft = pigame.PiTft()

screen = pygame.display.set_mode((320, 240))
screen.fill(WHITE)
pygame.display.set_caption("Robot Cone Drop Simulation")
pygame.mouse.set_visible(True)
pygame.display.update()
# clock = pygame.time.Clock()

# Fonts
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
btn_quit_rect = pygame.Rect(140, 180, 60, 40)

# Manual button setup
btn_manual_text = 'Manual Drop'
btn_manual_text_color = BLACK
btn_manual_color = WHITE
btn_manual_rect = pygame.Rect(240, 180, 60, 40)

# Variables
cone_count = 0
servo_index = 0
last_drop_time = time.time()
drop_interval = 2
rotation = False

def move_servo(index):
    servo_driver1.ChangeDutyCycle(servo_dc[index])
    time.sleep(0.5)

def drop_cone():
    global servo_index, rotation
    if not rotation:
        print("1\n")
        servo_index = 0
        rotation = True
        move_servo(servo_index)
    else:
        servo_index += 2
        print(f"2: servo {servo_index}\n")
        if servo_index >= 5:  # Changed from len(servo_dc) to 4
            rotation = False
            servo_index = 0  # Reset to initial position
            move_servo(servo_index)
        else:
            move_servo(servo_index)
    
    timestamp = time.strftime('%H:%M:%S')
    print(f"Dropped cone at {timestamp} - Servo position: {servo_index + 1}")


def draw_disk(surface):
    center = (160, 120)  # Center of the 320x240 screen
    outer_radius = 80    # Reduced to fit the smaller screen
    hole_radius = 10     # Slightly smaller holes
    hole_offset = outer_radius - 15
    num_holes = 5
    initial_offset = 270

    pygame.draw.circle(surface, BLACK, center, outer_radius, 2)

    for i in range(num_holes):
        angle = (initial_offset - i * (180 / (num_holes - 1))) % 360
        theta = math.radians(angle)
        x = center[0] + hole_offset * math.cos(theta)
        y = center[1] - hole_offset * math.sin(theta)
        color = RED if i == servo_index else WHITE
        pygame.draw.circle(surface, color, (int(x), int(y)), hole_radius)
        pygame.draw.circle(surface, BLACK, (int(x), int(y)), hole_radius, 2)
        hole_number_text = font_small.render(str(i + 1), True, BLACK)
        hole_text_rect = hole_number_text.get_rect(center=(int(x), int(y)))
        surface.blit(hole_number_text, hole_text_rect)

    pygame.draw.circle(surface, RED, center, 5)

def draw_buttons():
    # Draw the start button
    pygame.draw.rect(screen, btn_start_color, btn_start_rect)
    btn_start_surface = font_small.render(btn_start_text, True, btn_start_text_color)
    btn_start_text_rect = btn_start_surface.get_rect(center=btn_start_rect.center)
    screen.blit(btn_start_surface, btn_start_text_rect)

    # Draw the quit button
    pygame.draw.rect(screen, btn_quit_color, btn_quit_rect)
    btn_quit_surface = font_small.render(btn_quit_text, True, btn_quit_text_color)
    btn_quit_text_rect = btn_quit_surface.get_rect(center=btn_quit_rect.center)
    screen.blit(btn_quit_surface, btn_quit_text_rect)

    # Draw the quit button
    pygame.draw.rect(screen, btn_manual_color, btn_manual_rect)
    btn_manual_surface = font_small.render(btn_manual_text, True, btn_manual_text_color)
    btn_manual_text_rect = btn_manual_surface.get_rect(center=btn_manual_rect.center)
    screen.blit(btn_manual_surface, btn_manual_text_rect)


print("Starting the simulation... Press Ctrl+C to quit.")
code_running = True
motor_running = False
start_time = time.time()
servo_driver1.start(dc)
while code_running:
    time_check = time.time()
    if(time_check-start_time >= 30):
        code_running = False
    
    screen.fill(WHITE)
    draw_disk(screen)
    draw_buttons()
    pitft.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise KeyboardInterrupt
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            print(f"Mouse clicked at ({x}, {y})")
            if btn_start_rect.collidepoint(x, y):
                # servo_driver1.start(dc)
                motor_running = True
                print("Simulation started. Automatic cone drops enabled.")
            elif btn_quit_rect.collidepoint(x, y):
                motor_running = False
                code_running = False
                print("Simulation stopped. Automatic cone drops disabled.")
            elif btn_manual_rect.collidepoint(x, y):
                print("Manual drop triggered.")
                drop_cone()

    if motor_running:
        current_time = time.time()
        if current_time - last_drop_time >= drop_interval:
            print("Automatic drop interval reached.")
            drop_cone()
            last_drop_time = current_time

    pygame.display.flip()

print("Exiting the simulation. Goodbye!")

servo_driver1.stop()
GPIO.cleanup()
pygame.quit()
del pitft
sys.exit()

