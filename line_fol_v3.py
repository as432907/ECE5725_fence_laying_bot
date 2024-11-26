import RPi.GPIO as GPIO
import time

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering

# Set the comparator pin as input (to read the digital output)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Read the value of the comparator output pin (digital signal)
        #comparator_state = GPIO.input(21)
        
        # The LM393 comparator output is active low:
        # - LOW (0) means IN+ > IN- (object detected)
        # - HIGH (1) means IN- > IN+ (no object detected)
        
        #if comparator_state == GPIO.LOW:
        if GPIO.input(20) == GPIO.LOW:
            print("Object detected: IN+ > IN-")
        else:
            print("No object detected: IN- > IN+")
        
        # Delay for a short time (1 second)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nProgram interrupted by user")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()