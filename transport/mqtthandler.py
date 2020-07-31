import network
import time
import json
import gc
import uasyncio as asyncio
from umqtt.mqtt_as import MQTTClient
from transport.protocol_handler import ProtocolHandler

# Default "do little" coro for optional user replacement
async def eliza(*_):  # e.g. via set_wifi_handler(coro): see test program
    await asyncio.sleep_ms(20)

class MQTTHandler(ProtocolHandler):
    def __init__(self, hardware, config):
        super().__init__(hardware, config)


        self.server = config["mqtt_server"]
        self.port = config["mqtt_port"]
        self.clientid = config["mqtt_clientid"]
        self.userid = config["userid"]
        self.password = config["password"]
        self.topicprefix = config["topicprefix"]
        self.client = None

        # Wifi
        self.wifi_ssid = config["wifi_ssid"]
        self.wifi_password = config["wifi_pw"]
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wifi_connected = False

        # Setup the wifi connection
        self.setup_wifi()

        self.visual_indicator = None
        self.devicehandler = None       # the handle to all the devices

        # setup mqtt
        #self.client = MQTTClient(self.clientid, server=self.server, port=self.port,
        #    user=self.userid, password=self.password)

        config_mqtt = {
            'client_id':     self.clientid,
            'server':        self.server,
            'port':          0,
            'user':          self.userid,
            'password':      self.password,
            'keepalive':     60,
            'ping_interval': 0,
            'ssl':           False,
            'ssl_params':    {},
            'response_time': 10,
            'clean_init':    True,
            'clean':         True,
            'max_repubs':    4,
            'will':          None,
            'subs_cb':       self.received_cb,
            'wifi_coro':     eliza,
            'connect_coro':  self.conn_han,
            'ssid':          self.wifi_ssid,
            'wifi_pw':       self.wifi_password,
        }


        self.client = MQTTClient(config_mqtt)

        #set to mqtt callback
        #self.client.set_callback(self.received_cb)
        #self.client.connect()

        topic = self.topicprefix  + 'cmnd/+/+'
        topic = topic.encode()
        self.topic = topic 
        #self.client.subscribe(topic)
        print ("mqtt setup listening to ", topic)
    
    async def conn_han(self, client):
        await self.client.subscribe(self.topic, 1)

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
    
    #def set_visual_indicator(self, vi_cb):
    #    self.visual_indicator = vi_cb


    #def received_cb(self, topic, msg, retain, dup):
    def received_cb(self, topic, msg, retain):
        '''
        Default mqtt callback
        '''
        print("mqtt callback ", (topic, msg))
        print("free memory", gc.mem_free())

        # blink to indicate incoming message
        self.hardware.blink(5)

        # process incoming message
        # for mqtt, topic/devicename/acton will determine which device to 
        # handle the request
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
        
        # call the device to handle the request 
        status = device["instance"].handle_request(action, msg)
        status = json.dumps(status)
        print ("Status of request", action, status)
            
        #publish the status to the status queue
        status_topic= self.topicprefix + "stat/" + devicename + "/" + action
        self.status_result = {
            "topic": status_topic.encode(),
            "msg" : status.encode()
            }
        self.loop.create_task(self.publish_status(self.status_result))

        # blink to indicate status has been publish
        self.hardware.blink(5)
        
    async def publish_status(self, status_message):  
        msg_enc=status_message["msg"]
        topic=status_message["topic"]
        await self.client.publish(topic, msg_enc)


    def publish(self, topic, msg):
        msg_enc=msg.encode()
        topic=topic.encode()
        print ("pub command topic ", topic, msg_enc)
        result = {
            "topic": topic,
            "msg" : msg
            }
        self.loop.create_task(self.publish_status(result))


    def set_device(self, devicehandler):
        '''
        Set the list of device handler
        '''
        self.devicehandler = devicehandler

    def start(self):
        self.loop = asyncio.get_event_loop()
        try:
            self.loop.run_until_complete(main_loop(self.client))
        finally:
            self.client.close()  # Prevent LmacRxBlk:1 errors        

    
async def main_loop(client):
    await client.connect()
    
    while True:
        await asyncio.sleep(5)
