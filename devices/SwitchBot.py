import ubluetooth
from ubluetooth import BLE, UUID
from micropython import const
import utime
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

# org.bluetooth.service.environmental_sensing
_SWITCHBOT_UUID = ubluetooth.UUID('cba20d00-224d-11e6-9fb8-0002a5d5c51b')
_SWITCH_UUID= ubluetooth.UUID('cba20002-224d-11e6-9fb8-0002a5d5c51b')

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

commands = {
    'press' : '\x57\x01\x00',
    'on'    : '\x57\x01\x01',
    'off'   : '\x57\x01\x02',
    'status': '\x57\x02\x00',
    'none'  : '\x00\x00\x00',
}

class Device():
    def __init__(self, hardware, deviceconfig):
        
        self.hardware = hardware
        self.devicename = deviceconfig["devicename"]
        
        # the BLE must be turned on
        self.__ble = self.hardware.get_ble_handle()
        
        self.addr_type = None
        self.addr = None
        self.adv_type = None
        self.value_handle = 0x16
        self.status_handle = 0x13
        self.last_status_str = None
        self.ops_read = False
        self.ops_write = commands["none"]
        self.ops_complete =False
        self.battery = 0
        self.firmware = 0
        self.bot_status =0

        # connection paramaters        
        self.conn_handle = None
        self.connected = False
        self.connect_retry = 5
        self.connect_retry_timeout = 5000 # millisecond
        
        self.mac = deviceconfig["mac"]
        self.addrbinary = encode_mac(self.mac)   
    
    def bt_irq(self, event, data):
        if event == _IRQ_PERIPHERAL_CONNECT:
            # A successful gap_connect().
            self.conn_handle, self.addr_type, self.addr = data
            print('connected to peripheral complete switchbot', self.conn_handle)
            self.connected=True

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Connected peripheral has disconnected.
            #conn_handle, addr_type, addr = data
            print('disconnect to peripheral complete...')
            self.connected = False
            self.conn_handle = None

        elif event == _IRQ_GATTC_WRITE_DONE:
            # A gattc_write() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            
            conn_handle, value_handle, status = data
            #print ("_IRQ_GATTC_WRITE_DONE", self.ops_write)
            # when the status is successful, then read the status of last write operation
            if self.ops_write == commands["status"] :
                #print("Write Complete, reading the status handle")
                self.__ble.gattc_read(self.conn_handle, self.status_handle)

        elif event == _IRQ_GATTC_READ_RESULT:
            # A gattc_read() has completed.
            conn_handle, value_handle, char_data = data
            
            # to handle only read status 
            if self.ops_write == commands["status"]:
                self.ops_write = commands["none"]
                self.last_status_str = byte2hex(char_data)
                stat=char_data[0]
                self.bot_status = int(stat)
                self.ops_read=True

                if len(self.last_status_str) == 26:
                    #get the battery status
                    stat = char_data[1]
                    batt = int(stat)
                    self.battery = batt
                    
                    # get the firmware status
                    stat = char_data[2]
                    fw = int(stat)
                    self.firmware = fw

            else:
                print('_IRQ_GATTC_READ_RESULT', byte2hex(char_data))
        elif event == _IRQ_GATTC_READ_DONE:
            # A gattc_read() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, value_handle, status = data
            if status == 0:
                self.ops_complete = True
        else:
            print(" unhandled event: {}, data: {}".format(event, data))
            
        gc.collect()

    def connect(self):
        '''
        connect to ble device. There is a retry to connect self.connect_retry before
        returning connection fail

        return 0 if successful
        return 9 if connection failed after retry
        '''
        print ("Connecting to BLE Device....")
        self.__ble.irq(self.bt_irq)
        
        if self.connected == True:
            return 0
        connect_retry = 0
        while self.connected == False:
            try :
                if connect_retry < self.connect_retry:
                    self.__ble.gap_connect(1, self.addrbinary, self.connect_retry_timeout)
                    if connect_retry > 1 :
                        print ("retry...", connect_retry)  
                else:
                    print("BLE connection to device FAILED!")
                    break
                connect_retry += 1
                utime.sleep(self.connect_retry_timeout/1000)
            except OSError as exc:
                print ("OSError:", exc.args[0], connect_retry)
                connect_retry += 1
                
        return 9
    
    def disconnect(self):
        '''
        disconnect from ble device. 

        Normally the device will disconnect itself. Call this want to explicity disconnect
        '''        
        self.__ble.gap_disconnect(self.conn_handle)
        if self.connected == False:
            return 0
        else:
            return 9

    def press(self):
        '''
        Switch on/off the device. 

        ''' 
        self.connect()
        if self.connected == False :
            return 9
        self.__ble.gattc_write(self.conn_handle, self.value_handle, commands["press"], 1)
        return 0
    def on(self):
        self.connect()
        if self.connected == False :
            return 9
        self.__ble.gattc_write(self.conn_handle, self.value_handle, commands["on"], 1)
        return 0
    def off(self):
        self.connect()
        if self.connected == False :
            return 9
        self.__ble.gattc_write(self.conn_handle, self.value_handle, commands["off"], 1)
        return 0

    def getStatus(self):
        '''
        This is the subset of the implementation
        https://github.com/RoButton/switchbotpy 
        '''
        self.connect()
        if self.connected == False:
            return 9
        self.ops_write = commands["status"]
        self.__ble.gattc_write(self.conn_handle, self.value_handle, commands["status"], 1)
        # wait for status
        while self.ops_write == commands["status"]:
            pass
        self.ops_write = commands["none"] # reset the flag

        result = {}
        result["status"] =  self.bot_status
        result["battery"] = self.battery
        result["firmware"] = self.firmware
        return result

    def handle_request(self, cmnd, action):
        '''
        This function is required because it handle all the 
        incoming command and action

        For SwitchBot, the commands 
        press  
            return : successful - {"status":0} 
                     error - {"status": 9}
        getstatus  
            return : {"status":0, "battery":99, "firmware":49} 
        '''
        result = {}
        gc.collect()
        if cmnd =="press":
            if self.press() == 0:
                result["status"] = 0
                
            else:
                result["status"] = 9
                
        elif cmnd == "getstatus":
            result = self.getStatus()
        if self.connected == True:
            self.disconnect()
        return result

def test_switchbot():
    import json

    bt = BLE()
    bt.active(True)
    switchbot = SwitchBot(bt,"C6:23:6C:64:20:C1")
    status = switchbot.getStatus()
    print("status: ", status)
    switchbot.off()
    bt.active(False)

#test_switchbot()