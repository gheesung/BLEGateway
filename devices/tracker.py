import ubluetooth
from ubluetooth import BLE, UUID
from micropython import const
import utime, json
import binascii
import gc

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)


def decode_mac(addr):
    """
    Decode readable mac address 
    """
    assert isinstance(addr, bytes) and len(addr) == 6, ValueError("mac address value error")
    return ":".join(['%02X' % byte for byte in addr])

def encode_mac(mac):
    """
    Encode mac to addvertising addr
    """
    assert isinstance(mac, str) and len(mac) == 17, ValueError("mac address value error")
    return binascii.unhexlify(''.join( c for c in mac if  c not in ':' ))

def byte2hex(addr):
    """
    Convert byte to hex
    """
    return "".join(['%02X' % byte for byte in addr])

class Device():
    def __init__(self, hardware, deviceconfig):
        
        self.hardware = hardware
        self.devicename = deviceconfig["devicename"]
        
        # the BLE must be turned on
        self.__ble = self.hardware.get_ble_handle()
        
        self.addr_type = None
        self.addr = None
        self.adv_type = None
        self.batt_handle = 8
        self.alarm_handle = 11
        self.button_handle = 14
        self.last_status_str = None
        self.ops_read = False
        self.ops_complete =False
        self.read_done = False
        self.battery = 0

        # connection paramaters        
        self.conn_handle = None
        self.connected = False
        self.connect_retry = 5
        self.connect_retry_timeout = 5000 # millisecond
        
        self.deviceconfig = deviceconfig
        self.mac = deviceconfig["mac"]
        self.addrbinary = encode_mac(self.mac)

    def bt_irq(self, event, data):
        if event == _IRQ_PERIPHERAL_CONNECT:
            # A successful gap_connect().
            self.conn_handle, self.addr_type, self.addr = data
            print('connected to peripheral complete')
            self.connected=True
       

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Connected peripheral has disconnected.
            #conn_handle, addr_type, addr = data
            print('disconnect to peripheral complete...')
            self.connected = False
            self.conn_handle = None

        elif event == _IRQ_GATTC_WRITE_DONE:
            # A gattc_write() has completed.
            
            conn_handle, value_handle, status = data
            #print ("_IRQ_GATTC_WRITE_DONE ", value_handle, status)
            #self.__ble.gattc_read(self.conn_handle, 0x10)

        elif event == _IRQ_GATTC_READ_RESULT:
            # A gattc_read() has completed.
            conn_handle, value_handle, char_data = data
            #print('_IRQ_GATTC_READ_RESULT', value_handle, byte2hex(char_data))
            if value_handle == self.batt_handle:
                self.battery = int(char_data[0])

        elif event == _IRQ_GATTC_READ_DONE:
            # A gattc_read() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, value_handle, status = data
            self.read_done = True
        elif event == _IRQ_GATTC_NOTIFY:
            # A gattc_read() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, value_handle, notify_data = data
            print("Value Handle, data", value_handle, notify_data)

                
        else:
            print("Unhandled event: {}, data: {}".format(event, data))
            
        gc.collect()

    def connect(self):
    # check if it is disconnected
        print ("Connecting to BLE Device....")
        self.__ble.irq(self.bt_irq)
        
        if self.connected == True:
            return 0
        connect_retry = 0
        while self.connected == False:
            try:
                if connect_retry < self.connect_retry:
                    self.__ble.gap_connect(0, self.addrbinary, self.connect_retry_timeout)
                    if connect_retry > 1:
                        print ("retry...", connect_retry)  
                else:
                    print("BLE connection to device FAILED!")
                    break
                connect_retry += 1
                utime.sleep(self.connect_retry_timeout/1000)        
            except OSError as exc:
                print ("OSError:", exc.args[0], connect_retry)
                connect_retry += 1
            
        if connect_retry >= self.connect_retry :
            return 9
        return 0
    def disconnect(self):
        '''
        disconnect from ble device. 

        Normally the device will disconnect itself. Call this want to explicity disconnect
        '''        
        if self.conn_handle != None:
            self.__ble.gap_disconnect(self.conn_handle)

        if self.connected == False:
            return 0
        else:
            return 9

    def set_alarm(self, state):
        if self.connect() == 0:

            _DATA = bytes([0x00,0x00])
            if state == 'on' :
                print("alarm is on")
                _DATA = bytes([0x01,0x00])
            self.__ble.gattc_write(self.conn_handle, self.alarm_handle,_DATA,1)
            return 0
        else:
            return 9
    
    def getBatteryLevel(self):
        '''
        get the battery level.
        '''
        self.connect()
        if self.connected == False:
            return 9
        self.__ble.gattc_read(self.conn_handle, self.batt_handle)   
        timeout = utime.ticks_add(utime.ticks_ms(), 5000)
        while self.read_done == False:
            # to prevent going into infinite loop
            if utime.ticks_diff(timeout, utime.ticks_ms()) <= 0:
                self.read_done = True 
        
        if self.read_done == True:
            self.read_done = False
            return 0
        return 9

    def handle_request(self, cmnd, action):
        '''
        This function is required because it handle all the 
        incoming command and action

        For SwitchBot, the commands 
        press  
            return : successful - {"status":0} 
                     error - {"status": 9}
        getstatus  
            return : {"name": "MJ_HT_V1", "humidity": 73.6, "fw": "00.00.66", "result": 0, "battery": 60, "temperature": 31.1} 
        '''
        gc.collect()

        res = {}
        res["result"] = 9
        res["command"] = cmnd
        #print (cmnd, action)
        if cmnd == "alarm":
            if action == "on":
                self.set_alarm("on")
            else:
                self.set_alarm("off")
            res["result"] = 0 
            res["alarm"] = action
        elif cmnd == "getstatus":
            if self.getBatteryLevel() == 0:
                res["result"] = 0
                res["battery"] = self.battery
            else:
                res["result"] = 9
                res["battery"] = self.battery
        if self.connected == True:
            self.disconnect()
        print (res)
        if res["result"] == 0:
            self.display_result(res)
        return res
    
    def display_result(self, res):
        text = {}
        text["line1"] = self.deviceconfig["friendlyname"]
        text["line2"] = "Action: " + res["command"]
        if res["command"] == "alarm":
            text["line3"] = "Status: " + res["alarm"]
        elif res["command"] == "getstatus":
            text["line3"] = "Batt: " + str(res["battery"])
        self.hardware.display_result(text)

def test_tracker():
    with open('../config.json') as f:
        config=json.load(f)

    from hardware.m5stackfire import Hardware

    hardware = {}
    hardware = config["hardware"]
    hardware_config ={}
    hardware_config = config[hardware]
    fire = Hardware(hardware_config)
            
    # setup the devices
    devices = config["devices"]
    device_req_handler = None
    for device in devices:
        print (device["devicename"])
        if device["devicetype"] == "bletracker":
            device_req_handler = Device(fire, device)

    device_req_handler.connect()
    device_req_handler.alarm('off')
    device_req_handler.getBatteryLevel()
    print("battery:", device_req_handler.battery)

#test_tracker()