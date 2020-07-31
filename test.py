#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

BUZZ_1PIN=7
GPIO.setup(BUZZ_1PIN, GPIO.OUT)

try:  
    
    while 1: 
        i=0

        while i<=3:
            print(i)
            print('Buzzing')
            GPIO.output(BUZZ_1PIN, GPIO.HIGH)
            time.sleep(2);
            GPIO.output(BUZZ_1PIN, GPIO.LOW)
            time.sleep(2)
            i+=1
            

except KeyboardInterrupt:  
   print('Exit')


except Exception as e:
    print(e)

finally:

    GPIO.cleanup()