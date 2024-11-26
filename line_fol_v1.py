import RPi.GPIO as GPIO
import time

# ----Define GPIO pins for sensors--------------------------------
GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
sensor_values = [GPIO.input(21)]
#print("sensor values: ", sensor_values)
code_running =  True
while code_running:
    print("sensor values: ", sensor_values)
    if sensor_values == [0]:
        #print("sensor ON" )
        code_running = False
    # else: 
    #     print("sensor OFF" )
        

# --- Reset all the GPIO pins by setting them to LOW --------------------
GPIO.cleanup()