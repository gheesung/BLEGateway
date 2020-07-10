import network
import socket
import time
import json
#from umqtt.simple2 import MQTTClient
import gc

from transport.mqtthandler import MQTTHandler

from machine import Pin, Timer, reset
from hardware.button import Button
BUTTON_A_PIN = const(39)
class mqtt2bleGateway():
    """miio2mqttGateway
    
    The gateway converts mqtt request and send to/receive from BLE devices.
    """
    def __init__(self) :
        """Initialise the Gateway
        """        
        self.deviceconfig = {}
        self.device_req_handler = {}
        self.config = None
        self.client = None
        self.config = None
        self.transport = None # for now only mqtt
        self.devices = {}
        self.ble_activated = False
        self.ble_handle = None
        self.hardware =None

        # start the BLE
        #self.startBLE()

        print("Starting up mqtt2ble gateway....")
        

        # load the configuration
        with open('config.json') as f:
            self.config=json.load(f)

        # setup the hardware. The hardware need to be setup before the devices
        # because some devices require the hardware to be initialised. 
        # e.g. ble
        hardware = self.config["hardware"]
        if hardware == "m5stack_core":
            from hardware.m5stackcore import Hardware
        elif hardware == "ttgo_t_cell":
            from hardware.ttgotcell import Hardware
        elif hardware == "m5stack_fire":
            from hardware.m5stackfire import Hardware

        hardware_config = self.config[hardware]
        self.hardware = Hardware(hardware_config)

        # setup the transport layeran
        if self.config["transport"] == "mqtt":
            mqttconfig = self.config["mqtt"]
            #self.transport = MQTTHandler(mqttconfig,self.mqtt_recv_cb)
            self.transport = MQTTHandler(mqttconfig)
        
        # setup the devices
        devices = self.config["devices"]
        for device in devices:
            #start an instance of the Switchbot   
            if device["devicetype"] == "switchbot":
                from devices.switchbot import SwitchBot
                device["instance"] = SwitchBot(self.hardware, device["mac"])

            if device["devicetype"] == "xiaomitemp":
                from devices.mithermometer import MiThermometer
                device["instance"] = MiThermometer(self.hardware, device["mac"])
            
            # create a hashmap of devices
            devicename = device["devicename"]
            self.device_req_handler[devicename]=device

        # pass the device handler to the transport handler
        self.transport.devicehandler = self.device_req_handler



        # pass the transport and device handler to the hardware
        self.hardware.set_transport_handler(self.transport)
        
        device={}
        for device in self.device_req_handler:
            #devicename = device['devicename']
            print("Added :", device)
        
        # hardware device to indicate visually (if possible) when the setup is completed.
        self.transport.set_visual_indicator(self.hardware.blink)
        self.hardware.show_setupcomplete()

    def start(self) :
        self.transport.start()


            
    
def main():
    gw = mqtt2bleGateway()
    gw.start()

if __name__ == "__main__":
    main()