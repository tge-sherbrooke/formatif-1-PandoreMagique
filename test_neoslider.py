# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-seesaw", "adafruit-blinka", "rpi.gpio"]
# ///
"""Test du NeoSlider - Animation arc-en-ciel sur les LEDs."""

import board 
import time 
from rainbowio import colorwheel 
from adafruit_seesaw.seesaw import Seesaw 
from adafruit_seesaw import neopixel 

# Configuration NeoSlider
i2c = board.I2C()
neoslider = Seesaw(i2c, 0x30)
pixels = neopixel.NeoPixel(neoslider, 14, 4, pixel_order=neopixel.GRB)

# Position dans la roue des couleurs
color_pos = 0

while True:
    # Remplir les pixels avec la couleur actuelle
    pixels.fill(colorwheel(color_pos))
    
    # Avancer vers la couleur suivante
    color_pos = (color_pos + 1) % 256
    
    time.sleep(0.02)
