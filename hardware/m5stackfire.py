
from hardware.m5stackcore import Hardware
import json
import machine, neopixel
from micropython import const
'''
This setup is for M5stack Fire.

'''

_NEOPIXEL_PIN = const(15)
_NEOPIXEL_NUM = const(8)
class Hardware(Hardware):
    
    def __init__(self, config):
        super().__init__(config)
        self.np = self.np = neopixel.NeoPixel(machine.Pin(_NEOPIXEL_PIN),_NEOPIXEL_NUM,bpp=4)
    
    def show_setupcomplete(self):
        super().show_setupcomplete()
        self.blink(10)
        
    def blink(self, totalblink=5):
        n = self.np.n
        # fade in/out
        for i in range(0, 4 * 256, 8):
            for j in range(n):
                if (i // 256) % 2 == 0:
                    val = i & 0xff
                else:
                    val = 255 - (i & 0xff)
                self.np[j] = (val, 0, 0, 0)
            self.np.write()
        # clear
        for i in range(n):
            self.np[i] = (0, 0, 0, 0)
        self.np.write()        
        
def test_m5stackfire():
        # load the configuration
    with open('../config.json') as f:
        config=json.load(f)
    
    # setup the hardware. The hardware need to be setup before the devices
    # because some devices require the hardware to be initialised. 
    # e.g. ble
    hardware = {}
    hardware = config["hardware"]
    hardware_config ={}
    hardware_config = config[hardware]
    fire = Hardware(hardware_config)
    fire.blink()
#test_m5stackfire()