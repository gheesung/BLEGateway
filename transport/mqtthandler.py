
import json
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

