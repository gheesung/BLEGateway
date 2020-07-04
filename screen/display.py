from ili934xnew import ILI9341, color565
from machine import Pin, SPI
import m5stack
import glcdfont
import tt14
import tt24
import tt32

fonts = [glcdfont,tt14,tt24,tt32]

text = 'Now is the time for all good men to come to the aid of the party.'

power = Pin(m5stack.TFT_LED_PIN, Pin.OUT)
power.value(0)

spi = SPI(
    2,
    baudrate=40000000,
    miso=Pin(m5stack.TFT_MISO_PIN),
    mosi=Pin(m5stack.TFT_MOSI_PIN),
    sck=Pin(m5stack.TFT_CLK_PIN))

display = ILI9341(
    spi,
    cs=Pin(m5stack.TFT_CS_PIN),
    dc=Pin(m5stack.TFT_DC_PIN),
    rst=Pin(m5stack.TFT_RST_PIN),
    w=240,
    h=320,
    r=6)

display.erase()
display.set_pos(2,2)
#for ff in fonts:
#    display.set_font(ff)
#    display.print(text)

display.erase()
display.set_font(tt24)
display.print("BLE Gateway")