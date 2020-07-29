#!/usr/bin/env python3

import requests
import RPi.GPIO as GPIO
import time
from rpi_ws281x import PixelStrip, Color
from datetime import date
import socketio
import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file= logging.FileHandler(filename='tableErrorMGMT.log')
file.setLevel(logging.WARNING)

file2= logging.FileHandler(filename='Table.log')
file2.setLevel(logging.INFO)

logger.addHandler(file);
logger.addHandler(file2);


# standard Python
sio = socketio.Client()
PIR_PIN= 18
PIR2_PIN=5
PIR3_PIN=8
PIR4_PIN=27
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(PIR2_PIN, GPIO.IN)
GPIO.setup(PIR3_PIN, GPIO.IN)
GPIO.setup(PIR4_PIN, GPIO.IN)


LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 12   # GPIO pin connected to the pixels (18 uses PWM!).

LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

tableId="5e29fa071c9d4400001deed1"
#gets reservation  for an onSite customer corresponding to the table id
urlPayGet="http://192.168.1.178:5000/reservation/checkpay/5e29fa071c9d4400001deed1"

#gets status of the table(occupied or not) and the object id
urlGetTableStat="http://192.168.1.178:5000/table/5e29fa071c9d4400001deed1" #TESTED AND WORKING

#updates occupied field when PIR detects motion
urlPutTableOcc="http://192.168.1.178:5000/table/tableoccupancyStat/5e29fa071c9d4400001deed1" #TESTED AND WORKING

#deletes reservation
urlResDelete="http://192.168.1.178:5000/reservation/deletereserve/5e29fa071c9d4400001deed1"

rgbStart=0
pirOne=0
pirTwo=0
pirThree=0
pirFour=0
customValidate=0

def rgbTrigger():
    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
 
def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

@sio.event
def connect():
    logger.info("I'm connected!")

@sio.event
def connect_error():
    logger.error("The connection failed!")

@sio.event
def disconnect():
    logger.info("I'm disconnected!")   

#listens for alert event to start rgb lights..based on if the event data correlates with the tableID
@sio.on('triggerRgb')
def on_message(data):
    logger.info('RGB has been triggered')
    logger.info(data)
    logger.info(tableId)
    if(data==tableId):
        rgbStart=1

@sio.on('occTable')
def occ_message(data):
    logger.info('Table is occupied')
    if (data=='true'):
        getTabOcc= requests.get(urlGetTableStat)
        tabOccStat=getTabOcc.json()  
    
sio.connect('http://192.168.1.178:5000')


def pirControl():
    putTabOcc= requests.put(urlPutTableOcc)
    tabOcc=putTabOcc.json()
    sio.emit('tableOcc', 'true');
    logger.info(tabOcc)    


def MOTION(PIR_PIN):
    if GPIO.input(PIR_PIN):     # if pin input high  
        pirOne=1
    else:                  # if pin input low 
        pirOne=2

def MOTION_TWO(PIR2_PIN):
    if GPIO.input(PIR2_PIN):     # if pin input high  
        pirTwo=1
    else:                  # if pin input low 
        pirTwo=2

def MOTION_THREE(PIR3_PIN):
    if GPIO.input(PIR3_PIN):     # if pin input high  
        pirThree=1
    else:                  # if pin input low 
        pirThree=2

def MOTION_FOUR(PIR4_PIN):
    if GPIO.input(PIR4_PIN):     # if pin input high  
        pirFour=1
    else:                  # if pin input low 
        pirFour=2



try:
    GPIO.add_event_detect(PIR_PIN, GPIO.BOTH, callback=MOTION)
    GPIO.add_event_detect(PIR2_PIN, GPIO.BOTH, callback=MOTION_TWO)
    GPIO.add_event_detect(PIR3_PIN, GPIO.BOTH, callback=MOTION_THREE)
    GPIO.add_event_detect(PIR4_PIN, GPIO.BOTH, callback=MOTION_FOUR)

    rgbTrigger()

    while 1:   
               
        if rgbStart==1:
            logger.info('Color wipe animations.')
            colorWipe(strip, Color(255, 0, 0))  # Red wipe
            colorWipe(strip, Color(0, 255, 0))  # Blue wipe
            colorWipe(strip, Color(0, 0, 255))  # Green wipe
            logger.info('Theater chase animations.')
            theaterChase(strip, Color(127, 127, 127))  # White theater chase
            theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            
           
           # when lights are on and motion is detected at table
            if pirOne==1 or pirTwo==1 or pirThree==1 or pirFour==1:
                time.sleep(3.5)
                
                #check if motion is still detected to eliminate chance of error
                if pirOne==1 or pirTwo==1 or pirThree==1 or pirFour==1:                    
                    colorWipe(strip, Color(0,0,0), 10) #turn off lights 
                    rgbStart=0 
                    customValidate=1                  
                    pirControl()  #update occupied field to true for table
        elif rgbStart==0:
            sio.wait() 

        
        #if a customer accidentally takes a seat at the wrong table 
        # or if persons tries to move chairs from one table to another 
        # or if a person who wasnt validated slips through the cracks
        if (pirOne==1 or pirTwo==1 or pirThree==1 or pirFour==1) and customValidate==0:
            time.sleep(3.5)
            if (pirOne==1 or pirTwo==1 or pirThree==1 or pirFour==1) and customValidate==0: 
                sio.emit('wrongTable', 'true') #emit event to frontdesk

        #if pir does not detect movement while the occupied field is true
        # then wait a bit and check if there is still no motion
        if pirOne==2 and pirTwo==2 and pirThree==1 and pirFour==1 and tabOccStat['occupied'] is True:
            j=0        
            time.sleep(3.5)
            
            #counts the duration for which the customer has left the table
            # changes the reserve status of the table to unreserved if customer does not return in x minutes
            while pirOne==2 and pirTwo==2 and pirThree==1 and pirFour==1:

                j=j+1

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
                    logger.info(payStat)
                   
                    
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
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
    logger.exception('Exit Code')


except Exception as e:
    logger.exception(e)

finally:
    sio.disconnect()
    GPIO.cleanup()

 