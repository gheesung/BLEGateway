import network
import socket
import time
import json
from umqtt.simple2 import MQTTClient
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
        #self.buttonA = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=None),  
        #    callback=self.button_a_callback, trigger=Pin.IRQ_FALLING)
        # start the BLE
        self.startBLE()

        print("Starting up mqtt2ble gateway....")
        

        # load the configuration
        with open('config.json') as f:
            self.config=json.load(f)

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
                device["instance"] = SwitchBot(self.ble_handle, device["mac"])

            if device["devicetype"] == "xiaomitemp":
                from devices.mithermometer import MiThermometer
                device["instance"] = MiThermometer(self.ble_handle, device["mac"])
            
            # create a hashmap of devices
            devicename = device["devicename"]
            self.device_req_handler[devicename]=device

        # pass the device handler to the transport handler
        self.transport.devicehandler = self.device_req_handler

        # setup the hardware
        if self.config["hardware"] == "m5stack_core":
            from hardware.m5stackcore import M5Stack_core
            self.hardware = M5Stack_core()
            #self.hardware.set_callback(39, self.button_a_callback)
            print("loaded M5Stack_core")
        elif self.config["hardware"] == "ttgo-t-cell":
            from hardware.ttgotcell import TTGO_t_cell
            self.hardware = TTGO_t_cell()
            #self.hardware.set_callback(39, self.button_a_callback)

        # pass the transport and device handler to the hardware
        self.hardware.set_transport_handler(self.transport)
        
        device={}
        for device in self.device_req_handler:
            #devicename = device['devicename']
            print("Added :", device)
        
        # hardware device to indicate visually (if possible) when the setup is completed.
        self.transport.set_visual_indicator(self.hardware.blink)
        self.hardware.show_setupcomplete()

    def startBLE(self):
        if self.ble_activated == False:
            from ubluetooth import BLE

            bt = BLE()
            bt.active(True)
            self.ble_activated = True
            self.ble_handle = bt

    def start(self) :
        self.transport.start()

    def button_a_callback(self, pin):
        #print("Button A (%s) changed to: %r" % (pin, pin.value()))
        if pin.value() == 0 :
            
            device = self.device_req_handler["studyrmfan"]
            # handle the request
            self.transport.publish('bs/studyrm/ble/cmnd/studyrmfan/press', 'on')
            
            #status = device["instance"].handle_request("press", "on")
            print ("status")
    
    def button_b_callback(self, pin):
        #print("Button B (%s) changed to: %r" % (pin, pin.value()))
        if pin.value() == 0 :
            reset()
            
    
def main():
    gw = mqtt2bleGateway()
    gw.start()

if __name__ == "__main__":
    main()