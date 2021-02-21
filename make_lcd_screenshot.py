import ctypes
import os

from PIL import Image
from enigma import eDBoxLCD


LCD_SIZE = (400, 240)

lcd = eDBoxLCD.getInstance()

lcd_data_p_p_t = ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8 * (LCD_SIZE[0] * LCD_SIZE[1] * 4)))
lcd_data = str(bytearray(ctypes.cast(int(lcd.this) + 16, lcd_data_p_p_t).contents.contents))

img = Image.fromstring('RGBA', LCD_SIZE, lcd_data)
img.save('/tmp/lcd.png')
