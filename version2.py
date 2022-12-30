"""
Code for an egg scale. uses hx711 load cell and an LCD screen.
Scale breaks egg sizes into the following ranges:
0   no egg      0.00 - 1.49
1   Small       1.50 - 1.74oz   Red
2   Medium      1.75 - 1.99oz   Yellow
3   Large       2.00 - 2.24oz   Green
4   Extra Large 2.25 - 2.49oz   Orange
5   Jumbo       2.50+oz         Blue
"""

import RPi.GPIO as GPIO
import time
import sys
from HX711 import *
from lcd1602 import LCD1602
import pygame

# Force Python 3 ###########################################################

if sys.version_info[0] != 3:
    raise Exception("Python 3 is required.")

############################################################################

# globals
WIDTH = 600
HEIGHT = 600

RED = (255, 0, 0)
YELLOW = (255,233,0)
ORANGE = (254,80,0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)



#MIN_CHANGE is the minimum weight change (in oz) before values are updated
MIN_CHANGE = 0.1
#NUM_PASS is the number of measurements to let throgh when a change is detected
NUM_PASS = 3
#egg sizes by minimum
SMALL = 1.5
MEDIUM = 1.75
LARGE = 2.0
EXTRA_LARGE = 2.25
JUMBO = 2.5

RED_LED = 4 #red led is out of GPIO pin 4
YELLOW_LED = 12
GREEN_LED = 13
ORANGE_LED = 22
BLUE_LED = 26
LEDs = [RED_LED, YELLOW_LED, GREEN_LED, ORANGE_LED, BLUE_LED]
BUTTON_PIN = 27

#load cell object using gpio 5 and 6 
hx = SimpleHX711(5, 6, 383, 37890) #to calibrate, use file: 
							#/egg_scale/hx711_test/endail.calibrate.py

lcd = LCD1602() #go into LCD code to see which GPIO are being used

# Initializing pygame surface
# surface = pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE | pygame.SCALED )
surface = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN )

running = True

class Weight:
    def __init__(self):
        self.mode = 0
        self.current_weight = 0
        self.change_detected = False
        self.change_counter = 0
        self.mode_str = ["PEEWEE", "SMALL", "MEDIUM", "LARGE", "EXTRA LARGE", "JUMBO"]
        self.mode_color = [WHITE, RED, YELLOW, GREEN, ORANGE, BLUE]
        
        
    def update_weight(self, weight_oz):
        #first detect if there was a change in any case
        if abs(self.current_weight - weight_oz) > MIN_CHANGE:
            self.change_detected = True
            self.change_counter = 0
        if self.change_detected and self.change_counter > NUM_PASS:
            self.change_detected = False
        if self.change_detected:
            self.current_weight = weight_oz
            self.change_counter += 1
        else:
            pass
        if abs(self.current_weight) < MIN_CHANGE:
            return 0
        else:
            return self.current_weight
            
    def update_LEDs(self):
        current_mode = self.get_mode()
        current_mode = current_mode - 1
        for i in range(len(LEDs)):
            gpio_pin = LEDs[i]
            if i == current_mode:
                GPIO.output(gpio_pin, GPIO.HIGH)
            else:
                GPIO.output(gpio_pin, GPIO.LOW)
    
    def get_mode(self):
        if self.current_weight < SMALL: return 0
        if self.current_weight < MEDIUM: return 1
        if self.current_weight < LARGE: return 2
        if self.current_weight < EXTRA_LARGE: return 3
        if self.current_weight < JUMBO: return 4
        else: return 5
        
    def get_mode_string(self):
        if self.current_weight <= MIN_CHANGE:
            return "no"
        else:
            return(self.mode_str[self.get_mode()])
        
    def get_mode_color(self):
        if self.current_weight <= MIN_CHANGE:
            return BLACK
        else:
            return(self.mode_color[self.get_mode()])
        
weight = Weight() #define weign objuect to maintin state for filtering
        

def cleanAndExit():
    lcd.lcd_text("", 1)
    lcd.lcd_text("", 2)
    
    print("Cleaning...")
    GPIO.cleanup()
    print("Bye!")
    sys.exit()
    
def grams_to_oz(weight_grams):
    return weight_grams * 0.03527396
        


def setup():
    """
    code run once for load scale
    """
    hx.zero()                   # zero the cell
    
    """
    code run once for pygame
    """
  
    # Initializing Pygame
    pygame.init()
  
  
    # Initialing RGB Color 
    color = (255,0, 0)
  
    # Changing surface color
    surface.fill(color)
    pygame.display.flip()
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('Egg Scale')
    
    """
    cone run once to set up GPIO for LEDs
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(ORANGE_LED, GPIO.OUT)
    GPIO.setup(BLUE_LED, GPIO.OUT)
    
    GPIO.setmode(GPIO.BCM)         #Set GPIO pin numbering
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Enable input and pull up resistors



def loop():
    """
    code run continuosly
    """

    try:
        val = float(hx.weight(7))
        #get weight in onces, stabilized, and rounded to two decimals
        oz = weight.update_weight(grams_to_oz(val))
        oz = round(oz, 2)
        # print("weight", grams_to_oz(val))
        
        weight.update_LEDs()
        
        lcd.lcd_text(weight.get_mode_string() + " EGG", 1)
        lcd.lcd_text(str(oz) + "oz", 2)
        
        input_state = GPIO.input(BUTTON_PIN) #Read and store value of input to a variable
        if input_state == False:     #Check whether pin is grounded
            hx.zero()
            print('Zero Button Pressed')   #Print 'Button Pressed'
        
        font = pygame.font.Font(None, 150)
        text = font.render(weight.get_mode_string() + " = " + str(oz) + "oz", True, WHITE, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (surface.get_width() // 2, surface.get_height() // 2)
        surface.fill(weight.get_mode_color())
        surface.blit(text, text_rect)
        # Draws the surface object to the screen.
        pygame.display.update()

        #handle exiting the program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                cleanAndExit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    running = False
                    cleanAndExit()

        # time.sleep(.001)
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()


##################################

if __name__ == "__main__":

    setup()
    while running:
        loop()
