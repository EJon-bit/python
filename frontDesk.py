#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import socketio
import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file= logging.FileHandler(filename='CustomerMGMT.log')
file.setLevel(logging.WARNING)

file2= logging.FileHandler(filename='CustomerError.log')
file2.setLevel(logging.INFO)

logger.addHandler(file);
logger.addHandler(file2);

# standard Python
sio = socketio.Client()

IR_PIN=36
IR2_PIN=37

BUZZ_1PIN=7

GPIO.setmode(GPIO.BOARD)

GPIO.setup(IR_PIN, GPIO.IN)
GPIO.setup(IR2_PIN, GPIO.IN)
GPIO.setup(BUZZ_1PIN, GPIO.OUT)


irSequence1=0
irSequence2=0

approvedCount=0
exitDeclinedCount=0

#list for all customers who are trying to leave without payment
exitDeclinedCount=0

#to track all customers detected by the ir sensor whose entry has already been validated
approvedCount=0

@sio.event
def connect():
    logger.info("I'm connected!")

@sio.event
def connect_error():
    logger.error("The connection failed!")

@sio.event
def disconnect():
    logger.info("I'm disconnected!") 

#listens for event prevent false alarms at front desk when a validated customer tries to enter
@sio.event
def entryApproval(data):
    global approvedCount
    logger.info('An Approved customer is now enterring!')
    approvedCount=1

#event occurs when customers leave their a table without paying
@sio.event
def noticeDesk(data):
    global exitDeclinedCount
    logger.info('A customer may be attempting to leave without pay!')
    #counts the numer of customers currently trying to leave without pay
    exitDeclinedCount=1

sio.connect('http://192.168.1.178:5000')



def OBSTACLE(IR_PIN):
    #if 2nd (middle sensor) triggered before first
    global irSequence1    
    if irSequence2==1:
        irSequence1=2   
            
    else:
        #1st ir sensor is then person might be entering
        irSequence1=1
        logger.info('motion detected')

def OBSTACLE_TWO(IR2_PIN):
    #if 1st ir sonsor detects person before middle sensor
    global irSequence2
    if irSequence1==1 :
        irSequence2=2  

    else: 
        irSequence2=1
        logger.info('motion detected')



def eraseCounters():
    global irSequence1
    global irSequence2    
    irSequence1=0
    irSequence2=0
    logger.info('Counters ahve been erased')
    


try:
    GPIO.add_event_detect(IR_PIN, GPIO.FALLING, callback=OBSTACLE)
    GPIO.add_event_detect(IR2_PIN, GPIO.FALLING, callback=OBSTACLE_TWO)
    
    while 1: 
        i=0        
        if irSequence1==1 or (irSequence1==1 and irSequence2==2):
            eraseCounters()
            logger.info('Customer entering')

            #triggers alarm if person that has not been validated is trying to enter
            if approvedCount==0:
                sio.emit('unauthorized', 'true')
                while i<=3:
                    GPIO.output(BUZZ_1PIN, GPIO.HIGH)
                    time.sleep(2);
                    GPIO.output(BUZZ_1PIN, GPIO.LOW)
                    time,sleep(2)
                    i+=1
            #if customer has been validated wait 3 seconds then clear variable 
            elif approvedCount!=0:
                time.sleep(3)
                approvedCount=0

        elif irSequence2==1 or (irSequence2==1 and irSequence1==2):
            eraseCounters()
            logger.info('Customer Leaving')
            if exitDeclinedCount>0:
                sio.emit('noPay', 'leaving')#emit mesage to server to alert front desk of deceitful customers
                while i<=4:
                    GPIO.output(BUZZ_1PIN, GPIO.HIGH)
                    time.sleep(3);
                    GPIO.output(BUZZ_1PIN, GPIO.LOW)
                    time.sleep(2);
                    i+=1

        elif irSequence1==0 and irSequence2==0:            
            logger.info('nothing is happening')


except Exception as e:
    logger.exception(e)

finally:
    sio.disconnect()
    GPIO.cleanup()
