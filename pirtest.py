#!/usr/bin/env python3

#test PIR Sensors

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
PIR_PIN = 18
GPIO.setup(PIR_PIN, GPIO.IN)
pirOne=0

def MOTION(PIR_PIN):
    global pirOne
    if GPIO.input(PIR_PIN):     # if pin input high  
        pirOne=1
    else:                  # if pin input low 
        pirOne=2
    

print ('PIR Module Test (CTRL+C to exit)')
time.sleep(2)
print ('Ready')

try:
    GPIO.add_event_detect(PIR_PIN, GPIO.BOTH, callback=MOTION)

    while 1:        
        if pirOne==1:
            print ('Motion Detected!')
            time.sleep(0.5)
        elif pirOne==2:
            print ('Person has moved!')
            time.sleep(0.5)
        else:
            print ('No Motion Detected!')
            time.sleep(0.5)

              
        print('Pir One is', pirOne)
        

except KeyboardInterrupt:
    print ('Quit')
    GPIO.cleanup()