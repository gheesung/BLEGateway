import network
import time
import json
import gc

class ProtocolHandler():
    def __init__(self, hardware, config):
        self.config = config
        self.hardware = hardware        


        self.visual_indicator = None
        self.devicehandler = None       # the handle to all the devices
        