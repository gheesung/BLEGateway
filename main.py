import network
import socket
import time
import json
from umqtt.simple2 import MQTTClient
import gc
from devices.switchbot import SwitchBot
from transport.mqtthandler import MQTTHandler

#m5stickc specific
from machine import Pin, Timer, reset
from m5stickc.button import Button
BUTTON_A_PIN = const(37)
BUTTON_B_PIN = const(39)

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
        
        # m5stick c hardware specific
        self.activatebutton = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_a_callback, trigger=Pin.IRQ_FALLING)
        self.resetbutton = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=None),  
            callback=self.button_b_callback, trigger=Pin.IRQ_FALLING)

        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wifi_connected = False
       
        # start the BLE
        self.startBLE()

        print("Starting up mqtt2ble gateway....")
        

        # load the configuration
        with open('config.json') as f:
            self.config=json.load(f)

        # start Wifi
        while self.wlan_sta.isconnected() == False:
            self.connect_wifi(self.config["wifi_ssid"], self.config["wifi_pw"])
        # setup the transport layer
        if self.config["transport"] == "mqtt":
            mqttconfig = self.config["mqtt"]
            self.transport = MQTTHandler(mqttconfig,self.mqtt_recv_cb)
        
        # setup the devices
        devices = self.config["devices"]
        for device in devices:

            #start an instance of the Switchbot   
            if device["devicetype"] == "switchbot":
                device["instance"] = SwitchBot(self.ble_handle, device["mac"])
            # create a hashmap of devices
            devicename = device["devicename"] 
            self.device_req_handler[devicename]=device
    
    def connect_wifi(self, ssid, password):
        
        if self.wlan_sta.isconnected():
            return None
        print('Trying to connect to %s...' % ssid)
        self.wlan_sta.connect(ssid, password)
        for retry in range(100):
            self.wifi_connected = self.wlan_sta.isconnected()
            if self.wifi_connected:
                break
            time.sleep(0.1)
            print('.', end='')
        if self.wifi_connected:
            print('\nConnected. Network config: ', self.wlan_sta.ifconfig())
        else:
            print('\nFailed. Not Connected to: ' + ssid)


    def mqtt_recv_cb(self, topic, msg, retain, dup):
        print("mqtt callback ", (topic, msg, retain, dup))
        print("free memory", gc.mem_free())
        msg=str(msg.decode("utf-8","ignore"))
        topic=str(topic.decode("utf-8","ignore"))
        pathstr=topic[len(self.transport.topicprefix):]
        pathstr = pathstr.split("/")
        if len(pathstr) != 3 :
            print ("Invalid topic path")
            return
        devicename = pathstr[1]
        action=pathstr[2]
        device = self.device_req_handler[devicename]
        # handle the request
        status = device["instance"].handle_request(action, msg)
        self.transport.publish(devicename,action, status )
    

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
            
            status = device["instance"].handle_request("press", "on")
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