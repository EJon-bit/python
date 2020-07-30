#!/usr/bin/env python3

import requests
import RPi.GPIO as GPIO
import time
from rpi_ws281x import PixelStrip, Color
import socketio
from datetime import date
import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file= logging.FileHandler(filename='table2.log')

logger.addHandler(file);

sio = socketio.Client()

tableId="5e29fa071c9d4400001deed1"

urlPayGet="http://192.168.1.178:5000/reservation/checkpay/5e29fa071c9d4400001deed1"

#gets status of the table(occupied or not) and the object id
urlGetTableStat="http://192.168.1.178:5000/table/5e29fa071c9d4400001deed1" #TESTED AND WORKING

#updates occupied field when PIR detects motion
urlPutTableOcc="http://192.168.1.178:5000/table/tableoccupancyStat/5e29fa071c9d4400001deed1" #TESTED AND WORKING

#deletes reservation
urlResDelete="http://192.168.1.178:5000/reservation/deletereserve/5e29fa071c9d4400001deed1"

# LED strip configuration:
LED_COUNT = 56        # Number of LED pixels.
LED_PIN = 12         # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

GPIO.setmode(GPIO.BCM)
PIR_PIN=18
PIR2_PIN=8

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(PIR2_PIN, GPIO.IN)

#checks to keep tabs on PIR status
pirOne=0
pirTwo=0


rgbStart=0 #check var to keep tabs on state of RGB lights (i.e. whether on/off)

customValidate=0 #check var to differentiate between a valid customer at table and the wrong customer

def MOTION(PIR_PIN):
    global pirOne
    if GPIO.input(PIR_PIN):     # if pin input high  
        pirOne=1
        logger.info('Motion detected')
    else:                  # if pin input low 
        pirOne=2
        logger.info('Motion no Longer detected')
    
def MOTION_TWO(PIR2_PIN):
    global pirTwo
    if GPIO.input(PIR2_PIN):     # if pin input high  
        pirTwo=1
    else:                  # if pin input low 
        pirTwo=2

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
    logger.info("I'm connected!")

@sio.event
def connect_error():
    logger.info("The connection failed!")

@sio.event
def disconnect():
    logger.info("I'm disconnected!")   

#listens for alert event to start rgb lights..based on if the event data correlates with the tableID
@sio.on('triggerRgb')
def on_message(data):
    global rgbStart
    global tableId
    logger.info('RGB has been triggered')     
    if(data==tableId):        
        rgbStart=1      
        logger.info('data is equal to TableId')

#listens for even generated when customer reaches their table to get the occupancy status of the table
@sio.on('occTable')
def occ_message(data):
    logger.info('Table is occupied')
    if (data=='true'):
        global tabOccStat
        getTabOcc= requests.get(urlGetTableStat)
        tabOccStat=getTabOcc.json()  
        logger.info(tabOccStat['occupied'])

sio.connect('http://192.168.1.178:5000')

#updates Tables status to true when customer reaches their table after being validated at entrance
def pirControl():
    putTabOcc= requests.put(urlPutTableOcc)
    tabOcc=putTabOcc.json()
    sio.emit('tableOcc', 'true');
    logger.info(tabOcc)


try:   
    GPIO.add_event_detect(PIR_PIN, GPIO.BOTH, callback=MOTION)
    GPIO.add_event_detect(PIR2_PIN, GPIO.BOTH, callback=MOTION_TWO)
    GPIO.add_event_detect(PIR3_PIN, GPIO.BOTH, callback=MOTION_THREE)
    GPIO.add_event_detect(PIR4_PIN, GPIO.BOTH, callback=MOTION_FOUR)

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    logger.info('Press Ctrl-C to quit.')
    
    while 1:
        if rgbStart==1:
            logger.info('Color wipe animations.')        
            colorWipe(strip, Color(0, 255, 0))  # Blue wipe
            colorWipe(strip, Color(0, 0, 255))  # Green wipe
            logger.info('Theater chase animations.')
        
            theaterChase(strip, Color(127, 0, 0))  # Red theater chase
            theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
            time.sleep(0.2)

            # when lights are on and motion is detected at table
            if (pirOne==1 or pirTwo==1):
                time.sleep(0.5)
                
                #check if motion is still detected to eliminate chance of error
                if (pirOne==1 or pirTwo==1):  
                    logger.info('Person has arrived at table')                  
                    colorWipe(strip, Color(0,0,0), 10) #turn off lights 
                    rgbStart=0 
                    customValidate=1                  
                    pirControl()  #update occupied field to true for table
                    time.sleep(0.1)
                    
        elif rgbStart==0: 
            logger.info(customValidate)
            time.sleep(1)

            #if a customer accidentally takes a seat at the wrong table 
            # or if persons tries to move chairs from one table to another 
            # or if a person who wasnt validated slips through the cracks
            if ((pirOne==1 or pirTwo==1) and customValidate==0):
                time.sleep(3.5)
                if (pirOne==1 or pirTwo==1) and customValidate==0: 
                    sio.emit('wrongTable', 'true') #emit event to frontdesk
                    logger.info('wrong Table')

            #if pir does not detect movement while the occupied field is true
            # then wait a bit and check if there is still no motion    
            elif ((pirOne==2 and pirTwo==2) and tabOccStat['occupied'] is True):
                j=0   
                logger.info('A customer may be Leaving')     
                time.sleep(3.5)
                
                #counts the duration for which the customer has left the table
                # changes the reserve status of the table to unreserved if customer does not return in x minutes
                while (pirOne==2 and pirTwo==2):

                    j=j+1
                    logger.info('Value of J is', j)
                    putTabOcc= requests.put(urlPutTableOcc) #changes occupied status to false
                    tabOcc=putTabOcc.json()
                    logger.info(tabOcc)
                    

                    if j==1:
                        timeCheck_one= time.time()/60
                
                    else:
                        # constantly re-writes until the time since last detected motion is greater than the limit (1 minute)
                        timeCheck_two= time.time()/60 

                    timeDiff= timeCheck_two - timeCheck_one 

                    if timeDiff> 1:
                        pirOne=0
                        pirTwo=0
                        pirThree=0
                        pirFour=0
                        getPay= requests.get(urlPayGet)
                        payStat= getPay.json()
                        logger.info(payStat['paid'])
                    
                        
                        #checks if customer has made payment
                        if payStat['paid'] is True:
                            logger.info('Customer has left...Table to be re-assigned')
                                                    
                            requests.delete(urlResDelete)
                            logger.info('Reservation has been deleted')
                            customValidate=0

                            
                        elif payStat['paid'] is False:  
                            #sends customer details for customers who have not yet paid that may be attempting to leave  to server 
                            sio.emit('frontdeskNotice', 'A customer may be leaving without pay')

except KeyboardInterrupt:  
   logger.info('Exit')

except Exception(e):
    logger.exception(e)

finally:
    sio.disconnect()
    GPIO.cleanup()