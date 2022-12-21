import RPi.GPIO as GPIO
import time

RED_LED = 4 #red led is out of GPIO pin 4
YELLOW_LED = 12
GREEN_LED = 13
ORANGE_LED = 22
BLUE_LED = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(YELLOW_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(ORANGE_LED, GPIO.OUT)
GPIO.setup(BLUE_LED, GPIO.OUT)


for i in range(5):
 print("LED turning on.")
 GPIO.output(RED_LED, GPIO.HIGH)
 time.sleep(0.1)
 print("LED turning off.")
 GPIO.output(RED_LED, GPIO.LOW) 
 time.sleep(0.1)
 print("LED turning on.")
 GPIO.output(YELLOW_LED, GPIO.HIGH)
 time.sleep(0.1)
 print("LED turning off.")
 GPIO.output(YELLOW_LED, GPIO.LOW) 
 time.sleep(0.1)
 print("LED turning on.")
 GPIO.output(GREEN_LED, GPIO.HIGH)                                                                                                                                
 time.sleep(0.1)
 print("LED turning off.")
 GPIO.output(GREEN_LED, GPIO.LOW) 
 time.sleep(0.1)
 print("LED turning on.")
 GPIO.output(ORANGE_LED, GPIO.HIGH)
 time.sleep(0.1)
 print("LED turning off.")
 GPIO.output(ORANGE_LED, GPIO.LOW) 
 time.sleep(0.1)
 print("LED turning on.")
 GPIO.output(BLUE_LED, GPIO.HIGH)
 time.sleep(0.1)
 print("LED turning off.")
 GPIO.output(BLUE_LED, GPIO.LOW) 
 time.sleep(0.1)
