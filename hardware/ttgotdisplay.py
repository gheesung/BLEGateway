'''
This class handles the TTGO T-Display

Please note that the micropython needs to be recompiled to include the fast
ST7789 drivers

refer to https://github.com/russhughes/st7789_mpy
'''
from micropython import const
from machine import Pin, Timer, ADC, SPI
#from hardware.button import Button
from hardware.aswitch import Pushbutton as Button
from hardware.basehardware import BaseHardware
from hardware.blescanner import BLEScanner

import st7789 
import utime
import vga1_8x16 as font
BUTTON_A_PIN = const(35)
#BUTTON_B_PIN = const(0)
BATT_PIN = const(34)

colormap = {
    "PINK": st7789.color565(255, 128, 192),
    "ORANGE" : st7789.color565(255,128,64),
    "GREY" : st7789.color565(127, 127, 127),
    "TURQUOISE" : st7789.color565(0, 128, 128),
    "AZURE" : st7789.color565(0, 128, 255),
    "OLIVE" : st7789.color565(128, 128, 0),
    "PURPLE" : st7789.color565(128, 0, 128),
    "WHITE" : st7789.color565(255, 255, 255)
}
#


class Hardware(BaseHardware):
    
    def __init__(self, config) :
        self.config = config
        # TTGO hardware specific
        self.tft = st7789.ST7789(
            SPI(2, baudrate=30000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(19)),
            135,
            240,
            reset=Pin(23, Pin.OUT),
            cs=Pin(5, Pin.OUT),
            dc=Pin(16, Pin.OUT),
            backlight=Pin(4, Pin.OUT),
            rotation=3)        
        
        self.tft.init()
        self.tft.rotation(1)
        self.tft.fill(0)
        
        pin_a = Pin(BUTTON_A_PIN, mode=Pin.IN, pull=None)
        #pin_b = Pin(BUTTON_B_PIN, mode=Pin.IN, pull=None)
        
        self.buttonA = Button(pin=pin_a)
        
        self.buttonA.press_func(self.button_A_callback, (pin_a,))  # Note how function and args are passed
        
        
        #configure the battery reading
        self.vbat = ADC(Pin(BATT_PIN))
        self.vbat.atten(ADC.ATTN_0DB)
        self.vbat.width(ADC.WIDTH_12BIT)

        self.tranport_handler = None
        
        # Turn off backlit
        self.screen_power = Pin(4, Pin.OUT)
        
        super().__init__(config)
    
    def get_bat_voltage(self):
        '''
        Override the default battery voltage reading to return the voltage 
        level of the battery
        '''
        raw = self.vbat.read()
        volt = raw/4095 * 3.7
        volt = round(volt,2) 
        return volt

    def set_transport_handler(self, transport_handler):
        self.tranport_handler = transport_handler
    
    def blink(self, totalblink=5):
        count=0
        while count < totalblink:
            count +=1
        
    def show_setupcomplete(self):
        self.blink(10)

    def display_result(self, text):
        print("Display Result")
        self.tft.fill(0)
        
        self.tft.text( font, text["line1"], 0, 0, st7789.color565(255,255,255), st7789.color565(0,0,0))
        self.tft.text( font, text["line2"], 0, 20, st7789.color565(255,255,255), st7789.color565(0,0,0))
        self.tft.text( font, text["line3"], 0, 40, st7789.color565(255,255,255), st7789.color565(0,0,0))
        
        color = colormap[text["code"]]
        self.tft.fill_rect(180,80,50,50, color)

    def button_A_callback(self, pin):
        print("Button A (%s) changed to: %r" % (pin, pin.value()))
        if pin.value() == 0 :
            bat_level = self.get_bat_voltage()
            #device = self.device_req_handler["studyrmfan"]
            # handle the request
            topic = self.tranport_handler.topicprefix + 'cmnd/studyrmfan/press'
            self.tranport_handler.publish(topic, 'on')

    def button_B_callback(self, pin):
        print("Button B (%s) changed to: %r" % (pin, pin.value()))
        if pin.value() == 0 :
            bat_level = self.get_bat_voltage()
            # handle the request
            print ("bat level", bat_level)
            topic = self.tranport_handler.topicprefix + 'cmnd/studyrmtemp/getstatus'
            self.tranport_handler.publish(topic, 'on')           

    def screen_off(self):
        self.screen_power.value(0)
    
    def screen_on(self):
        self.screen_power.value(1)