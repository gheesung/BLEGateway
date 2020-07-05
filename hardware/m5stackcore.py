from micropython import const
from machine import Pin, Timer
from hardware.button import Button
from hardware.dummy import DummyHardware

#screen components
import sys
sys.path.append('/screen/m5stack')
import m5stack
from time import sleep
from ili9341 import Display, color565
from machine import Pin, SPI
from xglcd_font import XglcdFont

#button A - GPIO39
#button B - GPIO38
#button C - GPIP37
BUTTON_A_PIN = const(39)
BUTTON_B_PIN = const(38)
BUTTON_C_PIN = const(37)

class M5Stack_core(DummyHardware):
    
    def __init__(self) :
        # m5stick c hardware specific
        self.buttonA = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_A_callback, trigger=Pin.IRQ_FALLING)
        self.buttonB = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_C_callback, trigger=Pin.IRQ_FALLING)
        self.buttonC = Button(pin=Pin(BUTTON_C_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_C_callback, trigger=Pin.IRQ_FALLING)
        
        self.tranport_handler = None

        self.display = None
        self.screen_power = None
        self.header_font = None
        self.large_label_font = None
        self.small_label_font = None

        self.setup_screen()
    
    def set_callback(self, button, cb):
        if button == BUTTON_A_PIN:
            self.buttonA = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=None),  
                callback=cb, trigger=Pin.IRQ_FALLING)

    def button_A_callback(self, pin):
        #print("Button (%s) changed to: %r" % (pin, pin.value()))
        if pin.value() == 0 :
            
            #device = self.device_req_handler["studyrmfan"]
            # handle the request
            topic = self.tranport_handler.topicprefix + 'cmnd/studyrmfan/press'
            self.tranport_handler.publish(topic, 'on')
            

    def button_C_callback(self, pin):
        #print("Button (%s) changed to: %r" % (pin, pin.value()))
        if pin.value() == 0 :
            
            #device = self.device_req_handler["waterheater"]
            # handle the request
            topic = self.tranport_handler.topicprefix + 'cmnd/waterheater/press'
            self.tranport_handler.publish(topic, 'on')


    def setup_screen(self):
        self.screen_power = Pin(m5stack.TFT_LED_PIN, Pin.OUT)
        self.screen_power.value(0)
        spi = SPI(
            2,
            baudrate=40000000,
            miso=Pin(m5stack.TFT_MISO_PIN),
            mosi=Pin(m5stack.TFT_MOSI_PIN),
            sck=Pin(m5stack.TFT_CLK_PIN))    
        #display = Display(spi, dc=Pin(4), cs=Pin(16), rst=Pin(17))
        self.display = Display(
            spi,
            cs=Pin(m5stack.TFT_CS_PIN),
            dc=Pin(m5stack.TFT_DC_PIN),
            rst=Pin(m5stack.TFT_RST_PIN), width=320, height=240, rotation=0)
        self.display.clear()    

        self.header_font = XglcdFont('/screen/m5stack/fonts/Unispace12x24.c', 12, 24)
        self.large_label_font = XglcdFont('/screen/m5stack/fonts/IBMPlexMono12x24.c', 12, 24)
        self.small_label_font = XglcdFont('/screen/m5stack/fonts/ArcadePix9x11.c', 9, 11)
    
    def show_setupcomplete(self):
        self.home_page()

    def home_page(self):
        self.screen_power.value(0)
        self.display.draw_image('/images/blecanvas.raw',0,0,320,240)
        #self.display.draw_text(45, 203, 'Fan', self.large_label_font, color565(0, 0, 0), background=color565(255, 255, 255))
        #self.display.draw_text(135, 203, 'Temp', self.large_label_font, color565(0, 0, 0), background=color565(255, 255, 255))
        #self.display.draw_text(225, 203, 'Heater', self.large_label_font, color565(0, 0, 0), background=color565(255, 255, 255))
        self.screen_power.value(1)

#a=M5Stack_core()
#a.home_page()