from micropython import const
from machine import Pin, Timer
from hardware.button import Button
from hardware.dummy import DummyHardware
import utime

#button A - GPIO34
#button B - GPIO36
#button C - GPIP39
#LED - GPIO21
BUTTON_A_PIN = const(39)
BUTTON_B_PIN = const(36)
BUTTON_C_PIN = const(34)
LED = const(21)

class TTGO_t_cell(DummyHardware):
    
    def __init__(self) :
        # m5stick c hardware specific
        self.buttonA = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_A_callback, trigger=Pin.IRQ_FALLING)
        self.buttonB = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_C_callback, trigger=Pin.IRQ_FALLING)
        self.buttonC = Button(pin=Pin(BUTTON_C_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_C_callback, trigger=Pin.IRQ_FALLING)
        
        self.led = Pin(LED, mode=Pin.OUT)
        
        self.tranport_handler = None
    
    def set_pin_callback(self, button, cb):
        '''
        call this to override the PIN callback function
        '''
        if button == BUTTON_A_PIN:
            self.buttonA = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=None),  
                callback=cb, trigger=Pin.IRQ_FALLING)

    def set_transport_handler(self, transport_handler):
        self.tranport_handler = transport_handler
    
    def blink(self, totalblink=5):
        count=0
        while count < totalblink:
            self.led.value(1)
            utime.sleep(0.1)
            self.led.value(0)
            utime.sleep(0.1)
            count +=1
        
    def show_setupcomplete(self):
        self.blink(10)
        
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
    
