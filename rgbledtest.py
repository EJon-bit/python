#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
from rpi_ws281x import PixelStrip, Color
import socketio

sio = socketio.Client()

tableId="5e29fa071c9d4400001deed1"

# LED strip configuration:
LED_COUNT = 60        # Number of LED pixels.
LED_PIN = 12         # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

GPIO.setmode(GPIO.BCM)
PIR_PIN = 18
PIR2_PIN=5
PIR3_PIN=8
PIR4_PIN=27
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(PIR2_PIN, GPIO.IN)
GPIO.setup(PIR3_PIN, GPIO.IN)
GPIO.setup(PIR4_PIN, GPIO.IN)

pirOne=0
pirTwo=0
pirThree=0
pirFour=0
rgbStart=0

def MOTION(PIR_PIN):
    global pirOne
    if GPIO.input(PIR_PIN):     # if pin input high  
        pirOne=1
    else:                  # if pin input low 
        pirOne=2
    
def MOTION_TWO(PIR2_PIN):
    global pirTwo
    if GPIO.input(PIR2_PIN):     # if pin input high  
        pirTwo=1
    else:                  # if pin input low 
        pirTwo=2

def MOTION_THREE(PIR3_PIN):
    global pirThree
    if GPIO.input(PIR3_PIN):     # if pin input high  
        pirThree=1
    else:                  # if pin input low 
        pirThree=2

def MOTION_FOUR(PIR4_PIN):
    global pirFour
    if GPIO.input(PIR4_PIN):     # if pin input high  
        pirFour=1
    else:                  # if pin input low 
        pirFour=2

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=25):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=100, iterations=5):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")   

#listens for alert event to start rgb lights..based on if the event data correlates with the tableID
@sio.on('triggerRgb')
def on_message(data):
    global rgbStart
    global tableId
    print('RGB has been triggered')     
    if(data==tableId):        
        rgbStart=1
        # logger.info(rgbStart)
        print('data is equal to TableId')

@sio.on('occTable')
def occ_message(data):
    logger.info('Table is occupied')
    if (data=='true'):
        getTabOcc= requests.get(urlGetTableStat)
        tabOccStat=getTabOcc.json()  

sio.connect('http://192.168.1.178:5000')




try:   
    GPIO.add_event_detect(PIR_PIN, GPIO.BOTH, callback=MOTION)
    GPIO.add_event_detect(PIR2_PIN, GPIO.BOTH, callback=MOTION_TWO)
    GPIO.add_event_detect(PIR3_PIN, GPIO.BOTH, callback=MOTION_THREE)
    GPIO.add_event_detect(PIR4_PIN, GPIO.BOTH, callback=MOTION_FOUR)

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    
    while True:
        if rgbStart==1:
            print('Color wipe animations.')        
            colorWipe(strip, Color(0, 255, 0))  # Blue wipe
            colorWipe(strip, Color(0, 0, 255))  # Green wipe
            print('Theater chase animations.')
        
            theaterChase(strip, Color(127, 0, 0))  # Red theater chase
            theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
            time.sleep(0.2)

            if pirOne==1 or pirTwo==1 or pirThree==1 or pirFour==1:
                time.sleep(0.5)
                
                #check if motion is still detected to eliminate chance of error
                if pirOne==1 or pirTwo==1 or pirThree==1 or pirFour==1:  
                    print('Person has arrived at table')                  
                    colorWipe(strip, Color(0,0,0), 10) #turn off lights 
                    rgbStart=0 
                    time.sleep(0.1)
                    
        elif rgbStart==0: 
            if pirOne==2 or pirTwo==2 or pirThree==2 or pirFour==2:
                 print('Person has left table') 
            print('RGB is off') 
            time.sleep(1)

except KeyboardInterrupt:
   print('Exit')

finally:
    sio.disconnect()
    GPIO.cleanup()