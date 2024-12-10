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

# Initialize pygame and pigame for touchscreen support
pygame.init()
pitft = pigame.PiTft()

# Screen setup
screen = pygame.display.set_mode((320, 240))
screen.fill(WHITE)
pygame.mouse.set_visible(True)
pygame.display.update()

# Font setup
font_small = pygame.font.Font(None, 20)
font_mid = pygame.font.Font(None, 30)
font_big = pygame.font.Font(None, 50)

# Button setup
start_button = pygame.Rect(40, 180, 60, 40)
stop_button = pygame.Rect(120, 180, 60, 40)
manual_button = pygame.Rect(200, 180, 100, 40)

# Variables
running = False
cone_count = 0
disk_angle = 0
log = []
last_drop_time = time.time()
drop_interval = 2  # Seconds between automatic drops

# Functions
def log_message(message):
    """Log a message and add it to the on-screen log."""
    print(message)
    log.append(message)
    if len(log) > 10:
        log.pop(0)  # Keep the log to the last 10 entries

def drop_cone():
    """Simulates a cone drop by updating the disk angle."""
    global disk_angle, cone_count
    disk_angle = (disk_angle + 45) % 360
    cone_count += 1
    log_message(f"Dropped cone at angle {disk_angle} (Count: {cone_count})")

def draw_disk(surface, angle):
    """Draws the spinning disk with numbered holes."""
    center = (160, 100)
    radius = 60
    pygame.draw.circle(surface, BLACK, center, radius, 2)
    for i in range(8):
        theta = math.radians(i * 45 + angle)
        x = center[0] + radius * math.cos(theta)
        y = center[1] - radius * math.sin(theta)
        pygame.draw.circle(surface, WHITE, (int(x), int(y)), 10)
        pygame.draw.circle(surface, BLACK, (int(x), int(y)), 10, 2)

def draw_buttons():
    """Draw the control buttons."""
    pygame.draw.rect(screen, GREEN if running else RED, start_button)
    pygame.draw.rect(screen, RED, stop_button)
    pygame.draw.rect(screen, WHITE, manual_button)

    screen.blit(font_small.render("Start", True, BLACK), start_button.move(10, 10))
    screen.blit(font_small.render("Stop", True, BLACK), stop_button.move(10, 10))
    screen.blit(font_small.render("Manual", True, BLACK), manual_button.move(10, 10))

def draw_log():
    """Draw the on-screen log."""
    y = 10
    for entry in log:
        screen.blit(font_small.render(entry, True, BLACK), (10, y))
        y += 15

# Main loop
try:
    clock = pygame.time.Clock()
    while True:
        screen.fill(WHITE)

        draw_buttons()
        draw_disk(screen, disk_angle)
        draw_log()
        pygame.update()
        for event in pygame.event.get():
            if (event.type is MOUSEBUTTONUP):
                x, y = pygame.mouse.get_pos()
                print(f"Mouse down at ({x}, {y})")
            elif (event.type is MOUSEBUTTONDOWN):
                x, y = pygame.mouse.get_pos()
                print(f"Mouse down at ({x}, {y})")
                running = True
                log_message("Started simulation.")
            elif stop_button.collidepoint(x, y):
                running = False
                log_message("Stopped simulation.")
            elif manual_button.collidepoint(x, y):
                drop_cone()

        if running and time.time() - last_drop_time >= drop_interval:
            drop_cone()
            last_drop_time = time.time()

        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    pygame.quit()
    del pitft
    sys.exit()
