#!/usr/bin/env python3

#test PIR Sensors

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

PIR_PIN= 18

GPIO.setup(PIR_PIN, GPIO.IN)

pirOne=0

def MOTION(PIR_PIN):
    if GPIO.input(PIR_PIN):     # if pin input high  
        pirOne=1
        print('Pir  variable has a value of', pirOne)
    else:                  # if pin input low 
        pirOne=2
        print('Pir variable has a value of', pirOne)


try:
    GPIO.add_event_detect(PIR_PIN, GPIO.BOTH, callback=MOTION)

    while 1:

        if pirOne==1:
            print('Motion Detected')

        else:
            print('No motion Detected')

except KeyboardInterrupt:  
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
    print('Exit Code')


except Exception as e:
    print(e)

finally:
        
    GPIO.cleanup()