# Set up libraries and overall settings
import RPi.GPIO as GPIO  # Imports the standard Raspberry Pi GPIO library
import time   # Imports sleep (aka wait or pause) into the program
GPIO.setmode(GPIO.BCM) # Sets the pin numbering system to use the physical layout

# Set up pin 11 for PWM
GPIO.setup(26,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
p = GPIO.PWM(26, 50)     # Sets up pin 11 as a PWM pin
p.start(0)               # Starts running PWM on the pin and sets it to 0
time.sleep (2)  
p.ChangeDutyCycle(0)

# Move the servo back and forth
# code_running = True
# try:
#     for i in range(12):
#         p.ChangeDutyCycle(1)     # Changes the pulse width to 3 (so moves the servo)
#         time.sleep(2)                 # Wait 1 second
# except KeyboardInterrupt:
#     print("\nProgram interrupted by user")

# Clean up everything
p.stop()                 # At the end of the program, stop the PWM
GPIO.cleanup()           # Resets the GPIO pins back to defaults