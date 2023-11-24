import RPi.GPIO as GPIO
import socket
import re
import time 

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

Fwd_lmot_PWM = 13  #pin 13                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
Bwd_lmot_PWM = 19 #pin 19
Fwd_lmot_EN = 35  #pin 35
Bwd_lmot_EN = 37  #pin 37
Fwd_rmot_PWM = 12  #pin 12
Bwd_rmot_PWM = 18  #pin 18
Fwd_rmot_EN = 36  #pin 36
Bwd_rmot_EN = 38  #pin 38
Start_charge = 29
Fire_button = 31 
#setup firing pins 
GPIO.setup(Start_charge, GPIO.OUT)
GPIO.setup(Fire_button,GPIO.OUT)

GPIO.setup(Fwd_lmot_EN, GPIO.OUT)
GPIO.setup(Bwd_lmot_EN, GPIO.OUT)
GPIO.setup(Fwd_lmot_PWM, GPIO.OUT)
GPIO.setup(Bwd_lmot_PWM, GPIO.OUT)

GPIO.setup(Fwd_rmot_EN, GPIO.OUT)
GPIO.setup(Bwd_rmot_EN, GPIO.OUT)
GPIO.setup(Fwd_rmot_PWM, GPIO.OUT)
GPIO.setup(Bwd_rmot_PWM, GPIO.OUT)

lf_pwm = GPIO.PWM(Fwd_lmot_PWM, 100)
lb_pwm = GPIO.PWM(Bwd_lmot_PWM, 100)
rf_pwm = GPIO.PWM(Fwd_rmot_PWM, 100)
rb_pwm = GPIO.PWM(Bwd_rmot_PWM, 100)

GPIO.output(Fwd_lmot_EN, GPIO.HIGH)
GPIO.output(Bwd_lmot_EN, GPIO.HIGH)
GPIO.output(Fwd_rmot_EN, GPIO.HIGH)
GPIO.output(Bwd_rmot_EN, GPIO.HIGH)

numbers = [0,0,0,0,0,0]

def connectToRc():
	localPort   = 1069
	bufferSize  = 1024
	UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	UDPServerSocket.bind(('', localPort))
	print("UDP server: {} {}".format(socket.gethostbyname(socket.gethostname()), localPort))
	while(True):
		bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
		message = bytesAddressPair[0]
		address = bytesAddressPair[1]
		print(message)
		#UDPServerSocket.sendto(serverResponseInBytes, address)
		numbers = msgParser(message)
		lm, rm = getMotorSpeeds(numbers)
		print(str(lm) + ', ' + str(rm))
		runMotors(lm, rm)

def msgParser(message):
    pattern = r'\d+'
    numbers = re.findall(pattern, str(message))
    n = 0
    for i in numbers:
        numbers[n] = int(i)
        n = n+1
    return numbers
        
def getMotorSpeeds(numbers):
    rightmotor = 0
    leftmotor = 0

    if numbers[0] > 0 and numbers[1] == 0:
        #forwards
        if numbers[2] == 2 and numbers[3] ==1:
            rightmotor -= numbers[0]
            leftmotor += numbers[0]
        #backwards
        if numbers[2] == 2 and numbers[3] ==2:
            rightmotor += numbers[0]
            leftmotor -= numbers[0]

    if numbers[0] == 0 and numbers[1] > 0:
        #right
        if numbers[2] == 2 and numbers[3] ==2:
            rightmotor -= numbers[1]
            leftmotor -= numbers[1]
        #left
        if numbers[2] == 1 and numbers[3] ==2:
            rightmotor += numbers[1]
            leftmotor += numbers[1] 
    if numbers[4] == 1:
        GPIO.output(Start_charge,GPIO.HIGH)
        if numbers[5] == 1:
            GPIO.output(Fire_button, GPIO.HIGH)
    else:
        GPIO.output(Start_charge,GPIO.LOW)
        
    #if numbers[4] == 1 and numbers[5] == 1:
        #GPIO.output(Fire_button,GPIO.HIGH)
        #time.sleep(0.01)
        #GPIO.output(Start_charge,GPIO.LOW)

    if leftmotor>100:
        leftmotor = 100
    elif leftmotor<-100:
        leftmotor = -100
    if rightmotor>100:
        rightmotor = 100
    elif rightmotor<-100:
        rightmotor=-100
        
    return leftmotor, rightmotor

def runMotors(lm, rm):
    if lm==0 and rm==0:
        lf_pwm.start(0)
        lb_pwm.start(0)
        rf_pwm.start(0)
        rb_pwm.start(0)
    
    if lm>=0:
        lf_pwm.start(lm)
    else:
        lb_pwm.start(-lm)      
    if rm>=0:
        rf_pwm.start(rm)
    else:
        rb_pwm.start(-rm)
        
connectToRc()
