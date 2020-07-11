import network
import socket
import time
import json
from umqtt.simple2 import MQTTClient
import gc
from devices.switchbot import SwitchBot

wlan_sta = network.WLAN(network.STA_IF)

def do_connect(ssid, password):
    wlan_sta.active(True)
    if wlan_sta.isconnected():
        return None
    print('Trying to connect to %s...' % ssid)
    wlan_sta.connect(ssid, password)
    for retry in range(100):
        connected = wlan_sta.isconnected()
        if connected:
            break
        time.sleep(0.1)
        print('.', end='')
    if connected:
        print('\nConnected. Network config: ', wlan_sta.ifconfig())
    else:
        print('\nFailed. Not Connected to: ' + ssid)
    return connected 


class TransportHandler():
    def __init__ (self):
        self.received_msg =None
        self.response_msg = None

    def send_msg(self):
        print("derived class did not implement send_msg")

    def received_msg(self,param):
        print("derived class did not implement received_cb", param)

class MQTTHandler(TransportHandler):
    def __init__(self, config, callback=None):
        self.config = config
        self.server = config["mqtt_server"]
        self.port = config["mqtt_port"]
        self.clientid = config["mqtt_clientid"]
        self.userid = config["userid"]
        self.password = config["password"]
        self.topicprefix = config["topicprefix"]
        self.receiver_callback = None
        self.client = None

        self.client = MQTTClient(self.clientid, server=self.server, port=self.port,
            user=self.userid, password=self.password)
        if callback == None :
            #set to default callback
            self.client.set_callback(self.received_cb)
        else:
            self.client.set_callback(callback)
        self.client.connect()

        topic = self.topicprefix  + 'cmnd/+/+'
        #topic = self.topicprefix  + 'cmnd/#'
        topic = topic.encode()
        self.client.subscribe(topic)
        print ("mqtt setup listening to ", topic)

    def received_cb(self, topic, msg, retain, dup):
        print((topic, msg, retain, dup))
        param={}
        param["topic"]=topic
        param["msg"]=msg
        param["retain"]=retain
        param["dup"]=dup
    def publish(self, devicename, action, msg):

        pub_topic= self.topicprefix + "stat/" + devicename + "/" + action
        msg=json.dumps(msg)
        msg_enc=msg.encode()
        pub_topic=pub_topic.encode()
        print ("pub topic ", pub_topic, msg_enc)
        self.client.publish(pub_topic, msg_enc)
    def start(self):
        blocking_method=True
        while True:
            if blocking_method:
                # Blocking wait for message
                self.client.wait_msg()
            else:
                # Non-blocking wait for message
                self.client.check_msg()
                # Then need to sleep to avoid 100% CPU usage (in a real
                # app other useful actions would be performed instead)
                time.sleep(1)




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
        print("free memory2", gc.mem_free())
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

def main():
    gw = mqtt2bleGateway()
    gw.start()

if __name__ == "__main__":
    main()