import pygame
import pigame  # import pigame for touch support
import os
import sys
from pygame.locals import *
import time

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Setup environment for the framebuffer (required when using pigame)
os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')

'''
# --- Setup GPIO - Motor-------------------------------------------------
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

## ------- COUNTER ------------------------
GPIOBtns_ctr = [0,0,0,0]

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

# Panic stop button setup
btn_stop_radius = 40
btn_stop_text = 'STOP'
btn_stop_text_color = BLACK
btn_stop_pos = (160, 120)
btn_stop_color = RED

# Stop button Clicks
btn_stop_ctr = 0
btn_stop_press = False

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

# Left History Setup
history_text_color = BLACK
left_history = ['Left History', 'Stop 0', 'Stop 0', 'Stop 0']
right_history = ['Right History', 'Stop 0', 'Stop 0', 'Stop 0']

'''
# --- FUNCTIONS - DEFINITIONS --------------------------------------------------
'''
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

# Movement stages
STAGES = [ ("forward", 2),("stop", 1),("backward", 2),("stop", 1),("pivot_left", 2),("stop", 1),("pivot_right", 2),("stop", 1)]

# Function to move the robot
def move_robot():
    global current_stage, stage_time
    global current_time
    stage_name, stage_duration = STAGES[current_stage]
    dc = 100 if stage_name != "stop" else 0

    # Update the PWM and GPIO settings based on the current stage
    if stage_name == "backward":
            print("Forward")
            pwm_driver1.ChangeDutyCycle(dc)
            pwm_driver2.ChangeDutyCycle(dc)
            GPIO.output(AI_1_pin, GPIO.LOW)
            GPIO.output(AI_2_pin, GPIO.HIGH)
            GPIO.output(BI_1_pin, GPIO.HIGH)
            GPIO.output(BI_2_pin, GPIO.LOW)
            left_history_update = f"Clkwise {int(current_time)}"
            right_history_update = f"Counter-Clk {int(current_time)}"
            time.sleep(2)
    elif stage_name == "forward":
            print("Backward")
            pwm_driver1.ChangeDutyCycle(dc)
            pwm_driver2.ChangeDutyCycle(dc)
            GPIO.output(AI_1_pin, GPIO.HIGH)
            GPIO.output(AI_2_pin, GPIO.LOW)
            GPIO.output(BI_1_pin, GPIO.LOW)
            GPIO.output(BI_2_pin, GPIO.HIGH)
            left_history_update = f"Counter-Clk {int(current_time)}"
            right_history_update = f"Clkwise {int(current_time)}"
            time.sleep(2)
    elif stage_name == "pivot_right":
            print("pivot_left")
            pwm_driver1.ChangeDutyCycle(dc)
            pwm_driver2.ChangeDutyCycle(0)
            GPIO.output(AI_1_pin, GPIO.HIGH)
            GPIO.output(AI_2_pin, GPIO.LOW)
            left_history_update = f"Clkwise {int(current_time)}"
            right_history_update = f"Stop {int(current_time)}"
            time.sleep(2)
    elif stage_name == "pivot_left":
            print("pivot_right")
            pwm_driver1.ChangeDutyCycle(0)
            pwm_driver2.ChangeDutyCycle(dc)
            GPIO.output(BI_1_pin, GPIO.LOW)
            GPIO.output(BI_2_pin, GPIO.HIGH)
            left_history_update = f"Stop {int(current_time)}"
            right_history_update = f"Counter-Clk {int(current_time)}"
            time.sleep(2)
    elif stage_name == "stop":
            print("Stop")
            pwm_driver1.ChangeDutyCycle(dc)
            pwm_driver2.ChangeDutyCycle(dc)
            left_history_update = f"Stop {int(current_time)}"
            right_history_update = f"Stop {int(current_time)}"
            time.sleep(1)

    # Update history
    update_history(left_history, left_history_update)
    update_history(right_history, right_history_update)

    # Increment the stage time
    stage_time += 1

    # Move to the next stage if the current stage duration is over
    if stage_time >= stage_duration:
            current_stage = (current_stage + 1) % len(STAGES)  # Loop back to the first stage after the last one
            stage_time = 0  # Reset the stage time

'''
# --- MAIN VARIABLES --------------------------------------------------
'''
code_running = True
robot_moving = False # set this to true for autostart
start_time = time.time()
current_stage = 0
stage_time = start_time

'''
# --- MAIN EVENT LOOP -------------------------------------------------
'''

while code_running:
    current_time = time.time() - start_time

    m_screen.fill(WHITE)
    
    # Draw the stop button
    pygame.draw.circle(m_screen, btn_stop_color, btn_stop_pos, btn_stop_radius)
    btn_stop_surface = font_mid.render(btn_stop_text, True, btn_stop_text_color)
    btn_stop_rect = btn_stop_surface.get_rect(center=btn_stop_pos)
    m_screen.blit(btn_stop_surface, btn_stop_rect)

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

    # Draw Left & Right History
    render_history_list(m_screen, font_small, left_history, (40, 80), history_text_color)
    render_history_list(m_screen, font_small, right_history, (220, 80), history_text_color)
    pitft.update()
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            code_running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            print(f"Mouse down at ({x}, {y})")

            # Check if stop button
            distance = ((x - btn_stop_pos[0]) ** 2 + (y - btn_stop_pos[1]) ** 2) ** 0.5
            if distance <= btn_stop_radius:
                left_history_update = f"Stop {int(current_time)}"
                right_history_update = f"Stop {int(current_time)}"
                update_history(left_history,left_history_update)
                update_history(right_history,right_history_update)
                # Toggle 
                btn_stop_press = not btn_stop_press
                if btn_stop_press:
                    robot_moving = False
                    btn_stop_text = 'RUN'
                    btn_stop_color = GREEN
                    print("Motor Stopped")
                else:
                    robot_moving = True
                    btn_stop_text = 'STOP'
                    btn_stop_color = RED
                    print("Running")
                btn_stop_ctr += 1  

            # Start Robot Button
            if btn_start_rect.collidepoint(x,y): 
                robot_moving = True 
            # QUIT Screen Button
            if btn_quit_rect.collidepoint(x, y):
                print("Quit button pressed")
                robot_moving = False
                code_running = False

    if not GPIO.input(GPIOBtns[3]):
        print("Quitting Program")
        code_running = False   
        time.sleep(0.2)

    if(current_time>=100):
        code_running = False
    if btn_stop_press is True:
         robot_moving is False
         pwm_driver1.ChangeDutyCycle(0)
         pwm_driver2.ChangeDutyCycle(0)
    elif robot_moving is True:
        move_robot()

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
