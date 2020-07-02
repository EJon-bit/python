import requests
import RPi.GPIO as GPIO
import time
import socketio

# standard Python
sio = socketio.Client()
IR_PIN= 16
IR2_PIN=36
IR3_PIN=37

BUZZ_1PIN=7
BUZZ_2PIN=15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IR_PIN, GPIO.IN)
GPIO.setup(IR2_PIN, GPIO.IN)
GPIO.setup(IR3_PIN, GPIO.IN)
GPIO.setup(BUZZ_1PIN, GPIO.OUT)
GPIO.setup(BUZZ_2PIN, GPIO.OUT)

irSequence1=0
irSequence2=0
irSequence3=0


#list for all customers who are trying to leave without payment
exitDeclinedCount=0

#to track all customers detected by the ir sensor whose entry has already been validated
approvedCount=0

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
     print("I'm disconnected!") 

#listens for event prevent false alarms at front desk when a validated customer tries to enter
@sio.event
def entryApproval(data):
    print('An Approved customer is now enterring!')
    approvedCount=data

@sio.event
def noticeDesk(data):
    print('A customer may be attempting to leave without pay!')
    #counts the numer of customers currently trying to leave without pay
    exitDeclinedCount=data

sio.connect('http://localhost:5000')

sio.wait()



def OBSTACLE(PIR_PIN):
    #if last (3rd) ir sensor detected customer then middle sensor or just middle then this
    if irSequence2==2 or irSequence2==3:
        irSequence1=2
        print('Person Leaving')
    else:
        #1st ir sensor is then person might be entering
        irSequence1=1
    

def OBSTACLE_TWO(PIR2_PIN):
    #if 1st ir sonsor detects person before middle sensor
    if irSequence1==1 :
        irSequence2=1

    #if 3rd sensor detetects person before middle sensor
    elif irSequence3==1:
        irSequence2=2

    else: 
        irSequence2==3
    

def OBSTACLE_THREE(PIR2_PIN):
    #if 1st sensor then 2nd detected person
    if irSequence2==1:
        irSequence3=2
    else:
        irSequence3=1

def eraseCounters():
    irSequence1=0
    irSequence2=0
    irSequence3=0


try:
    GPIO.add_event_detect(IR_PIN, GPIO.LOW, callback=OBSTACLE)
    GPIO.add_event_detect(IR2_PIN, GPIO.LOW, callback=OBSTACLE_TWO)
    GPIO.add_event_detect(IR3_PIN, GPIO.LOW, callback=OBSTACLE_THREE)
    while 1: 
        i=0

        if irSequence1==1 or irSequence2==1 or irSequence3==1:
            eraseCounters()
            print('Customer entering')

            #triggers alarm if person that has not been validated is trying to enter
            if approvedCount==0:
                sio.emit('unauthorized', 'true')
                while i<=3:
                    GPIO.output(BUZZ_1PIN, GPIO.HIGH)
                    time.sleep(0.5);
                    GPIO.output(BUZZ_1PIN, GPIO.LOW)
                    i+=1
            #if customer has been validated wait 3 seconds then clear variable 
            elif approvedCount!=0:
                time.sleep(3)
                approvedCount=0

        elif irSequence2==2 or irSequence1==2:
            eraseCounters()
            print('Customer Leaving')
            if exitDeclinedCount>0:
                sio.emit('noPay', 'leaving')#emit mesage to server to alert front desk of deceitful customers
                while i<=5:
                    GPIO.output(BUZZ_2PIN, GPIO.HIGH)
                    time.sleep(0.2);
                    GPIO.output(BUZZ_2PIN, GPIO.LOW)
                    time.sleep(0.2);
                    i+=1


        elif  irSequence3==1 and irSequence1==1:
            eraseCounters()
            print('A Customer is Leaving while another enters')

            if approvedCount==0 or exitDeclinedCount>0:
                sio.emit('noPay', 'both')
                while i<=2:
                    GPIO.output(BUZZ_1PIN, GPIO.HIGH)
                    time.sleep(0.3);
                    GPIO.output(BUZZ_1PIN, GPIO.LOW)
                    time.sleep(0.5)
                    i+=1

           