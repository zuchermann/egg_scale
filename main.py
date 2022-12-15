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
from hx711 import HX711
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
NUM_PASS = 10
#egg sizes by minimum
SMALL = 1.5
MEDIUM = 1.75
LARGE = 2.0
EXTRA_LARGE = 2.25
JUMBO = 2.5


#load cell object using gpio 5 and 6 
hx = HX711(5, 6)

lcd = LCD1602()

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
        self.mode_str = ["NO", "SMALL", "MEDIUM", "LARGE", "EXTRA_LARGE", "JUMBO"]
        self.mode_color = [BLACK, RED, YELLOW, GREEN, ORANGE, BLUE]
        
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
        if self.current_weight < MIN_CHANGE:
            return 0
        else:
            return self.current_weight
    
    def get_mode(self):
        if self.current_weight < SMALL: return 0
        if self.current_weight < MEDIUM: return 1
        if self.current_weight < LARGE: return 2
        if self.current_weight < EXTRA_LARGE: return 3
        if self.current_weight < JUMBO: return 4
        else: return 5
        
    def get_mode_string(self):
        return(self.mode_str[self.get_mode()])
        
    def get_mode_color(self):
        return(self.mode_color[self.get_mode()])
        

weight = Weight()

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
    hx.set_offset(8428205.1875) # values generated from calibration.py
    hx.set_scale(384.35)        # rerun that script to recalibrate load
    hx.tare()                   # cell
    
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


def loop():
    """
    code run continuosly
    """

    try:
        val = hx.get_grams(1)
        oz = weight.update_weight(grams_to_oz(val))
        oz = round(oz, 2)
        print("weight", grams_to_oz(val))
        
        lcd.lcd_text(weight.get_mode_string() + " EGG", 1)
        lcd.lcd_text(str(oz) + "oz", 2)
        
        font = pygame.font.Font(None, 75)
        text = font.render(weight.get_mode_string() + " = " + str(oz) + "oz", True, WHITE, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (surface.get_width() // 2, surface.get_height() // 2)
        surface.fill(weight.get_mode_color())
        surface.blit(text, text_rect)
        # Draws the surface object to the screen.
        pygame.display.update()

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
