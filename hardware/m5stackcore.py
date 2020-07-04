from micropython import const
from machine import Pin, Timer
from hardware.button import Button
from hardware.dummy import DummyHardware

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
            callback=self.button_callback, trigger=Pin.IRQ_FALLING)
        self.buttonB = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_callback, trigger=Pin.IRQ_FALLING)
        self.buttonC = Button(pin=Pin(BUTTON_C_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_callback, trigger=Pin.IRQ_FALLING)
    
    def set_callback(self, button, cb):
        if button == BUTTON_A_PIN:
            self.buttonA = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=None),  
                callback=cb, trigger=Pin.IRQ_FALLING)

    def button_callback(self, pin):
        print("Button (%s) changed to: %r" % (pin, pin.value()))

    
