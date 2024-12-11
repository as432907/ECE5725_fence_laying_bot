import pygame
import pigame  # import pigame for touch support
import os
import sys
from pygame.locals import *
import math
import time

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
# --- Setup the display -------------------------------------------------
'''
# Initialize pygame and pigame for touchscreen support
pygame.init()
pitft = pigame.PiTft()

m_screen = pygame.display.set_mode((320, 240))
m_screen.fill(WHITE)
pygame.mouse.set_visible(True)
pygame.display.update()

# Font setup
font_small = pygame.font.Font(None, 20)
font_mid = pygame.font.Font(None, 30)
font_big = pygame.font.Font(None, 50)

# Buttons
start_button = pygame.Rect(50, 400, 100, 50)
stop_button = pygame.Rect(200, 400, 100, 50)
manual_button = pygame.Rect(350, 400, 150, 50)

# Variables
running = False
cone_count = 0
disk_angle = 0  # Current angle of the disk
log = []  # Store drop history
last_drop_time = time.time()
drop_interval = 2  # Seconds between automatic drops

import logging

# Set up logging to a file
logging.basicConfig(
    filename="simulation.log",  # Log file name
    level=logging.INFO,         # Logging level
    format="%(asctime)s - %(message)s",  # Log message format
    datefmt="%Y-%m-%d %H:%M:%S"  # Timestamp format
)

def log_and_print(message):
    """Logs the message to the file and prints it to the terminal."""
    print(message)       # Print to terminal
    logging.info(message)  # Write to log file

def drop_cone():
    """Simulates a cone drop by updating the disk angle and log."""
    global disk_angle, cone_count
    disk_angle = (disk_angle + 45) % 360  # Move disk by 45 degrees
    cone_count += 1
    timestamp = time.strftime('%H:%M:%S')
    log_entry = f"Dropped cone ({timestamp})"
    log.append(log_entry)
    print(log_entry)  # Log to the terminal

# def draw_disk(surface, angle):
#     """Draw the spinning disk."""
#     center = (320, 240)
#     pygame.draw.circle(surface, BLACK, center, 100, 2)
#     # Draw 8 segments
#     for i in range(8):
#         theta = math.radians(i * 45 + angle)
#         x = center[0] + 100 * math.cos(theta)
#         y = center[1] - 100 * math.sin(theta)
#         pygame.draw.line(surface, RED if i == 0 else BLACK, center, (x, y), 2)

def draw_disk(surface, angle):
    """
    Draws a rotating disk with a boundary circle, 7 lines to holes, 7 holes at 45-degree intervals,
    and a start marker to indicate the rotating direction.
    """
    # Create a temporary surface to hold the disk and elements
    temp_surface = pygame.Surface((200, 200), pygame.SRCALPHA)  # A 200x200 surface with transparency
    temp_surface.fill((0, 0, 0, 0))  # Fill with transparent background

    # Disk parameters
    center = (100, 100)  # Center of the disk (on the temporary surface)
    outer_radius = 90  # Outer radius of the disk (scaled for the temp surface)
    hole_radius = 15  # Radius of each hole (scaled)
    hole_offset = outer_radius - 20  # Offset where the holes are placed (slightly inward)
    
    # Draw the outer boundary circle
    pygame.draw.circle(temp_surface, BLACK, center, outer_radius + 10, 2)  # Slightly larger boundary
    # Draw the main disk
    pygame.draw.circle(temp_surface, BLACK, center, outer_radius, 2)

    # Draw 7 lines and holes at 45-degree intervals (clockwise rotation)
    for i in range(7):  # Only 7 lines and holes
        theta = math.radians(-i * 45 + angle)  # Negative angle for clockwise rotation
        line_x = center[0] + hole_offset * math.cos(theta)  # End point of the line (to the hole)
        line_y = center[1] - hole_offset * math.sin(theta)  # Same offset for holes

        # Draw the line from the center to the hole position
        pygame.draw.line(temp_surface, BLACK, center, (int(line_x), int(line_y)), 2)

        # Draw the hole at the same position
        hole_x = center[0] + hole_offset * math.cos(theta)
        hole_y = center[1] - hole_offset * math.sin(theta)
        pygame.draw.circle(temp_surface, WHITE, (int(hole_x), int(hole_y)), hole_radius)
        pygame.draw.circle(temp_surface, BLACK, (int(hole_x), int(hole_y)), hole_radius, 2)  # Hole border
        
        # Label each hole with a number (1 to 7)
        hole_number_text = font_small.render(str(i + 1), True, BLACK)
        hole_text_rect = hole_number_text.get_rect(center=(int(hole_x), int(hole_y)))
        temp_surface.blit(hole_number_text, hole_text_rect)

    # # Add a start marker (e.g., a small circle) at the "start point"
    # start_marker_offset = outer_radius - 10  # Position the marker closer to the edge
    # # Adjust the marker to align with the first hole (45 degree increments)
    # marker_index = int((angle % 360) / 45)  # Find which hole the marker should align with
    # start_marker_angle = math.radians(-marker_index * 45)  # Adjusted angle for the marker's position
    # start_marker_x = center[0] + start_marker_offset * math.cos(start_marker_angle)
    # start_marker_y = center[1] - start_marker_offset * math.sin(start_marker_angle)
    # pygame.draw.circle(temp_surface, RED, (int(start_marker_x), int(start_marker_y)), 5)  # Small red circle marker

    # Rotate the entire temp_surface by the given angle (negative for clockwise)
    rotated_surface = pygame.transform.rotate(temp_surface, -angle)  # Negative for clockwise rotation
    
    # Get the new center of the rotated image (to center it correctly on the main screen)
    rotated_rect = rotated_surface.get_rect(center=(320, 240))

    # Blit the rotated surface onto the main screen
    surface.blit(rotated_surface, rotated_rect.topleft)

    # Display the rightmost hole number
    rightmost_hole_index = int((angle % 360) / 45)  # The index of the rightmost hole
    rightmost_hole_number = (rightmost_hole_index + 1)  # Hole numbers are 1-7, not 0-6
    rightmost_text = font_big.render(str(rightmost_hole_number), True, RED)
    surface.blit(rightmost_text, (300, 10))  # Display the number at the top right of the screen

def draw_buttons():
    """Draw control buttons."""
    pygame.draw.rect(screen, GREEN if running else RED, start_button)
    pygame.draw.rect(screen, RED, stop_button)
    pygame.draw.rect(screen, WHITE, manual_button)

    start_text = font_mid.render("Start", True, BLACK)
    stop_text = font_mid.render("Stop", True, BLACK)
    manual_text = font_mid.render("Manual Drop", True, BLACK)

    screen.blit(start_text, start_button.move(15, 10))
    screen.blit(stop_text, stop_button.move(20, 10))
    screen.blit(manual_text, manual_button.move(10, 10))

def draw_log():
    """Display the drop log."""
    y = 10
    for entry in log[-10:]:  # Show last 10 entries
        log_text = font_small.render(entry, True, BLACK)
        screen.blit(log_text, (10, y))
        y += 20

try:
    print("Starting the simulation... Press Ctrl+C to quit.")
    while True:
        screen.fill(WHITE)
        draw_disk(screen, disk_angle)
        draw_buttons()
        draw_log()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                log_and_print(f"Mouse clicked at ({x}, {y})")
                if start_button.collidepoint(x, y):
                    running = True
                    log_and_print("Simulation started. Automatic cone drops enabled.")
                elif stop_button.collidepoint(x, y):
                    running = False
                    log_and_print("Simulation stopped. Automatic cone drops disabled.")
                elif manual_button.collidepoint(x, y):
                    log_and_print("Manual drop triggered.")
                    drop_cone()  # Perform a manual cone drop

        if running:
            current_time = time.time()
            if current_time - last_drop_time >= drop_interval:
                log_and_print("Automatic drop interval reached.")
                drop_cone()
                last_drop_time = current_time

        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    log_and_print("Exiting the simulation. Goodbye!")
finally:
    pygame.quit()
    sys.exit()
