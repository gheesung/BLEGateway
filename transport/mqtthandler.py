import network
import time
import json
import gc

from umqtt.simple2 import MQTTClient


class MQTTHandler():
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
        self.devicehandler = None

        # Wifi
        self.wifi_ssid = config["wifi_ssid"]
        self.wifi_password = config["wifi_pw"]
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wifi_connected = False

        # Setup the wifi connection
        self.setup_wifi()

        self.visual_indicator = None
        
        # setup mqtt
        self.client = MQTTClient(self.clientid, server=self.server, port=self.port,
            user=self.userid, password=self.password)
        if callback == None :
            #set to default callback
            self.client.set_callback(self.received_cb)
        else:
            self.client.set_callback(callback)
        self.client.connect()

        topic = self.topicprefix  + 'cmnd/+/+'
        
        topic = topic.encode()
        self.client.subscribe(topic)
        print ("mqtt setup listening to ", topic)

    def setup_wifi(self):
        if self.wlan_sta.isconnected():
            return None
        print('Trying to connect to %s...' % self.wifi_ssid)
        self.wlan_sta.connect(self.wifi_ssid, self.wifi_password)
        for retry in range(100):
            self.wifi_connected = self.wlan_sta.isconnected()
            if self.wifi_connected:
                break
            time.sleep(0.1)
            print('.', end='')
        if self.wifi_connected:
            print('\nConnected. Network config: ', self.wlan_sta.ifconfig())
        else:
            print('\nFailed. Not Connected to: ' + self.wifi_ssid)
            raise Exception ("Unable to connect to WIFI")
    
    def set_visual_indicator(self, vi_cb):
        self.visual_indicator = vi_cb
        
    def received_cb(self, topic, msg, retain, dup):
        '''
        Default mqtt callback
        '''
        print("mqtt callback ", (topic, msg, retain, dup))
        print("free memory", gc.mem_free())
        self.visual_indicator(5)
        msg=str(msg.decode("utf-8","ignore"))
        topic=str(topic.decode("utf-8","ignore"))
        pathstr=topic[len(self.topicprefix):]
        pathstr = pathstr.split("/")
        if len(pathstr) != 3 :
            print ("Invalid topic path")
            return
        devicename = pathstr[1]
        action=pathstr[2]
        device = self.devicehandler[devicename]
        # handle the request and publish the status
        status = device["instance"].handle_request(action, msg)
        self.publish_status(devicename,action, status )
        self.visual_indicator(5)
    
    def publish_status(self, devicename, action, msg):

        pub_topic= self.topicprefix + "stat/" + devicename + "/" + action
        msg=json.dumps(msg)
        msg_enc=msg.encode()
        pub_topic=pub_topic.encode()
        print ("pub topic ", pub_topic, msg_enc)
        self.client.publish(pub_topic, msg_enc)
    def publish(self, topic, msg):
        msg_enc=msg.encode()
        topic=topic.encode()
        print ("pub topic ", topic, msg_enc)
        self.client.publish(topic, msg_enc)

    def set_device(self, devicehandler):
        '''
        Set the list of device handler
        '''
        self.devicehandler = devicehandler

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

