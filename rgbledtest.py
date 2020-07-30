#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
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
GPIO.setup(PIR_PIN, GPIO.IN)
pirOne=0
rgbStart=0

def MOTION(PIR_PIN):
    global pirOne
    if GPIO.input(PIR_PIN):     # if pin input high  
        pirOne=1
    else:                  # if pin input low 
        pirOne=2
    


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=30):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=100, iterations=10):
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


sio.connect('http://192.168.1.178:5000')

# time.sleep(2)
# print ('Ready')

# Main program logic follows:
try:   
    GPIO.add_event_detect(PIR_PIN, GPIO.BOTH, callback=MOTION) 
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

            if pirOne==1:
                time.sleep(0.5)
                
                #check if motion is still detected to eliminate chance of error
                if pirOne==1:  
                    print('Person has arrived at table')                  
                    colorWipe(strip, Color(0,0,0), 10) #turn off lights 
                    rgbStart=0 
                 
                    
        elif rgbStart==0:  
            print('RGB is off') 
            time.sleep(1)

except KeyboardInterrupt:
   print('Exit')

finally:
    sio.disconnect()
    GPIO.cleanup()