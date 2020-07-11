import ubluetooth
from ubluetooth import BLE, UUID, FLAG_NOTIFY, FLAG_READ, FLAG_WRITE 
from micropython import const
import utime, json, binascii , gc
from hardware.bleradio import BLERadio
from transport.protocol_handler import ProtocolHandler

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

class BLEScanner(ProtocolHandler):
    def __init__(self, hardware, deviceconfig):
        super().__init__(hardware, deviceconfig)
        
        self.hardware = hardware
        self.__ble = self.hardware.get_blehandle()
        
        self.__ble.irq(self.bt_irq)
        self.addr_type = None
        self.addr = None
        self.adv_type = None
        self.ops_read = False
        self.ops_complete =False
        self.read_done = False
        # connection paramaters        
        self.conn_handle = None
        self.connected = False

        self.ble_scaninterval = deviceconfig["scan_interval"]
        self.ble_scanwindow = deviceconfig["scan_window"]

        self.deviceconfig = deviceconfig

        self.setup_bledevices()

        #self.mac = deviceconfig["mac"]
        #self.addrbinary = encode_mac(self.mac)

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
        elif event == _IRQ_SCAN_RESULT:
            # A single scan result.
            addr_type, addr, adv_type, rssi, adv_data = data
            
            self.received_cb(addr, rssi, adv_data)

        elif event == _IRQ_SCAN_DONE:
            # Scan duration finished or manually stopped.
            pass

        elif event == _IRQ_GATTC_WRITE_DONE:
            # A gattc_write() has completed.
            
            conn_handle, value_handle, status = data
            #print ("_IRQ_GATTC_WRITE_DONE ", value_handle, status)
            #self.__ble.gattc_read(self.conn_handle, 0x10)

        elif event == _IRQ_GATTC_READ_RESULT:
            # A gattc_read() has completed.
            conn_handle, value_handle, char_data = data

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

    def scan(self):
        self.__ble.gap_scan(0, self.ble_scaninterval, self.ble_scanwindow )


    def setup_bledevices(self):
        self.bledevices = {}
        self.bledevices_mac=[]
        
        for device in self.deviceconfig["ble_devices"]:
            mac = device["mac"]
            self.bledevices[mac] = device
            self.bledevices_mac.append(mac)

    def received_cb(self, addr, rssi, adv_data):
        '''
        BLE Scan result
        '''
        mac = decode_mac(addr)
        if mac not in self.bledevices_mac:
            return 
            
        adv_data = byte2hex(adv_data)
        print('_IRQ_SCAN_RESULT Result', rssi, decode_mac(addr), adv_data)
        print("free memory", gc.mem_free())

        
        # blink to indicate incoming message
        self.hardware.blink(5)

        # process incoming message
        # pass the request to the BLE Adv Handler
        # handle the request
        device = self.devicehandler["bleadv_handler"]
        print ("device Name", device["devicename"])

        data = {}
        data["mac"] = mac
        data["payload"] = adv_data
        data["rssi"] = rssi
        data["devicename"] = device["devicename"]
        data["friendlyname"] = device["friendlyname"]
        data["deviceprotocol"] = device["deviceprotocol"]
        data["devicetype"] = device["devicetype"]

        deviceinst = device["instance"]
        # cann the device to handle the request and publish the status
        status = deviceinst.handle_request('decode_ad_data', data)
    
        # blink to indicate status has been publish
        self.hardware.blink(5)
        
    def start(self):
        self.scan()

        while True:
            utime.sleep_ms(10000)

def test_bletracker():
    with open('../config.json') as f:
        config=json.load(f)

    from hardware.m5stackfire import Hardware
    
    hardware = {}
    hardware = config["hardware"]
    hardware_config ={}
    hardware_config = config[hardware]
    firehw = Hardware(hardware_config)

    #from transport.bletracker import BLEScanner
    bletracker_config = config["blescanner"]
    transport = BLEScanner(firehw, bletracker_config)
    transport.start()
#test_bletracker()