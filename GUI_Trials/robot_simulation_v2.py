import pygame
import math
import sys
import time

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((640, 480))  # Windowed mode
pygame.display.set_caption("Robot Cone Drop Simulation")
clock = pygame.time.Clock()

# Fonts
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
    Draws a disk with stationary tiny circles and rotates only the larger disk circle.
    """
    # Parameters
    center = (320, 240)  # Center of the disk
    outer_radius = 100  # Outer radius of the large circle
    hole_radius = 15  # Radius of the tiny circles
    hole_offset = outer_radius - 20  # Offset of the tiny circles from the center

    # Draw the rotating large circle
    pygame.draw.circle(surface, BLACK, center, outer_radius, 2)

    # Draw the stationary tiny circles at 45-degree intervals
    for i in range(7):
        theta = math.radians(i * 45)  # Fixed positions for the tiny circles
        x = center[0] + hole_offset * math.cos(theta)
        y = center[1] - hole_offset * math.sin(theta)
        pygame.draw.circle(surface, WHITE, (int(x), int(y)), hole_radius)
        pygame.draw.circle(surface, BLACK, (int(x), int(y)), hole_radius, 2)  # Border for the tiny circles

        # Label each tiny circle with its number
        hole_number_text = font_small.render(str(i + 1), True, BLACK)
        hole_text_rect = hole_number_text.get_rect(center=(int(x), int(y)))
        surface.blit(hole_number_text, hole_text_rect)

    # Draw a rotating marker or highlight on the large circle
    marker_angle = math.radians(-angle)  # Convert to radians for clockwise rotation
    marker_x = center[0] + (outer_radius - 10) * math.cos(marker_angle)
    marker_y = center[1] - (outer_radius - 10) * math.sin(marker_angle)
    pygame.draw.circle(surface, RED, (int(marker_x), int(marker_y)), 5)


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
