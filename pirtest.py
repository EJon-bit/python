#!/usr/bin/env python3

#test PIR Sensors

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
PIR_PIN = 18
GPIO.setup(PIR_PIN, GPIO.IN)
pirOne=0

def MOTION(PIR_PIN):
    pirOne=1
    print(pirOne)
    

print ('PIR Module Test (CTRL+C to exit)')
time.sleep(2)
print ('Ready')

try:
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=MOTION)
    while 1:
        if pirOne is 1:
            print ('Motion Detected!')
        else:
            print ('No Motion Detected!')

        pirOne=0
        time.sleep(5)

except KeyboardInterrupt:
    print ('Quit')
    GPIO.cleanup()