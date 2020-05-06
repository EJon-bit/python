import requests
import RPi.GPIO as GPIO
import time
from neopixel import *
from datetime import date

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN)
GPIO.setup(29, GPIO.IN)

LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
 
#gets reserve all reservations for this table and the reserve date and check if any customer is onsite
urlonSiteGet="http://localhost:5000/reservation/checkonsite/5e29fa9c1c9d4400001deed2"

#gets status of the table(occupied or not) and the object id
urlGetTableStat="http://localhost:5000/table/5e29fa9c1c9d4400001deed2" #TESTED AND WORKING

#updates occupied field to turn offRGB when PIR detects motion
urlPutTableOcc="http://localhost:5000/table/tableoccupancyStat/5e29fa9c1c9d4400001deed2" #TESTED AND WORKING

#updates reserved field if PIR no longer detects motion
urlPutReserve="http://localhost:5000/table/tableavailability/2/5e29fa9c1c9d4400001deed2" #TESTED & WORKING

#deletes reservation
urlResDelete="http://localhost:5000/reservation/deletereserve/5e29fa9c1c9d4400001deed2"



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

def pirControl():
    putTabOcc= requests.put(urlPutTableOcc)
    tabOcc=putTabOcc.json()
    print(tabOcc)
    # if tabOcc['occupied'] is True:
    #     print('Customer has arrived') 
  

def rgbControl():
    pirSensetab=1
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    while pirSensetab==1:
        print ('Color wipe animations.')
        colorWipe(strip, Color(255, 0, 0))  # Red wipe
        colorWipe(strip, Color(0, 255, 0))  # Blue wipe
        colorWipe(strip, Color(0, 0, 255))  # Green wipe
        print ('Theater chase animations.')
        theaterChase(strip, Color(127, 127, 127))  # White theater chase
        theaterChase(strip, Color(127,   0,   0))  # Red theater chase
        theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
        print ('Rainbow animations.')
        pir_oneCheck=GPIO.input(12)
        pir_twoCheck=GPIO.input(29)

        if pir_oneCheck==1 or pir_twoCheck==1:

            time.sleep(3.5)
            pir_oneCheck=GPIO.input(12)
            pir_twoCheck=GPIO.input(29)

            if pir_oneCheck==1 or pir_twoCheck==1:
                pirSensetab=0
                colorWipe(strip, Color(0,0,0), 10)
                pirControl()


while True:    

    onSiteGet= requests.get(urlonSiteGet)
    onSiteStat= onSiteGet.json()
    print (onSiteStat)

    getTabOcc= requests.get(urlGetTableStat)
    tabOccStat=getTabOcc.json()

    if (onSiteStat['onSite'] is True and tabOccStat['occupied'] is False):
        rgbControl()

    pir_oneCheck=GPIO.input(12)
    pir_twoCheck=GPIO.input(29)

    
    if pir_oneCheck==0 and pir_twoCheck==0 and tabOccStat['occupied'] is True:
        j=0        
        time.sleep(3.5)
        pir_oneCheck=GPIO.input(12)
        pir_twoCheck=GPIO.input(29)

        while pir_oneCheck==0 and pir_twoCheck==0:
            pir_oneCheck=GPIO.input(12)
            pir_twoCheck=GPIO.input(29)

            j=j+1

            putTabOcc= requests.put(urlPutTableOcc)
            tabOcc=putTabOcc.json()
            print(tabOcc)
            k=j

            if j==1:
                timeCheck_one= time.time()/60
           
            else:
                timeCheck_two= time.time()/60

            timeDiff= timeCheck_two - timeCheck_one

            if timeDiff> 1:
                print ('Customer has left...Table to be re-assigned')

                #updates 'reserved' status of table to false if there are no queued reservation
                putTabResStat= requests.put(urlPutReserve)
                tabResStat=putTabResStat.json()

                #check if person has made payment
                #if not bring to front desk attention


 