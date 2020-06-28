import ubluetooth
from ubluetooth import BLE, UUID
from micropython import const
import utime
import binascii
import re
import gc

_HANDLE_READ_NAME = 0x03
_HANDLE_READ_BATTERY = 0x18
_HANDLE_READ_VERSION = 0x24
_HANDLE_READ_SENSOR_DATA = 0x10

MI_TEMPERATURE = "temperature"
MI_HUMIDITY = "humidity"
MI_BATTERY = "battery"

_MITemp_UUID = ubluetooth.UUID('0000fe95-0000-1000-8000-00805f9b34fb')

import utime
IRQ_CENTRAL_CONNECT = const(1)
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

import binascii

def decode_mac(addr):
    """
    Decode readable mac address from advertising addr
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
    Decode readable mac address from advertising addr
    """
    return "".join(['%02X' % byte for byte in addr])

class MiThermometer:
    """"
    A class to read data from Mi thermometer sensors.
    """
    def __init__(self, ble, mac):    
        self.__ble = ble
        #print("ble activated")
        #self.__ble.config(rxbuf=256)
        #self.__ble.irq(self.bt_irq)
        
        self.read_done = False
        self.__cache = None
        self.mitempdata = {}
        
        self.conn_handle = None
        self.connect_retry_timeout = 5000 # millisecond
        self.connect_retry = 5
        self.name = None
        self.connected = False
        self.addrbinary = encode_mac(mac)

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
            if value_handle == _HANDLE_READ_BATTERY:
                self.__cache=char_data
                #print ("Battery Level ", int(char_data[0]))
                self.mitempdata["battery"] = int(char_data[0])

            if value_handle == _HANDLE_READ_NAME:
                self.name = ''.join(chr(n) for n in char_data)
                #print('Sensor Name ', self.name)
                self.mitempdata["name"] = self.name
            if value_handle == _HANDLE_READ_VERSION:
                self._firmware_version = "".join(map(chr, char_data))
                #print (self._firmware_version)
                self.mitempdata["fw"] = self._firmware_version

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
            #print('_IRQ_GATTC_NOTIFY', value_handle, byte2hex(notify_data)) 
            self.__cache=notify_data
            self._parse_data()
            self.read_done = True

                
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

    def getSensorData(self):
        self.connect()
        if self.connected == False:
            return 9
        self.read_done = False
        _DATA_MODE_CHANGE = bytes([0x01,0x00])
        self.__ble.gattc_write(self.conn_handle, 0x10,_DATA_MODE_CHANGE,1)
        while self.read_done == False:
            pass
        self.read_done = False
        #self.__ble.gattc_read(self.conn_handle, 58)
    
    def _parse_data(self):
        """Parses the byte array returned by the sensor.
        The sensor returns a string with 14 bytes. Example: "T=26.2 H=45.4\x00"
        """
        data = self.__cache
        res = dict()
        #print (byte2hex(data))
        res[MI_TEMPERATURE], res[MI_HUMIDITY] = re.sub("[TH]=", '', data[:-1].decode()).split(' ')
        
        res[MI_TEMPERATURE] = float(res[MI_TEMPERATURE])
        res[MI_HUMIDITY] = float(res[MI_HUMIDITY])
        self.mitempdata[MI_TEMPERATURE] = res[MI_TEMPERATURE] 
        self.mitempdata[MI_HUMIDITY] = res[MI_HUMIDITY] 

        #print (self.mitempdata)
        #return self.mitempdata

    def getName(self):
        self.connect()
        if self.connected == False:
            return 9
        self.__ble.gattc_read(self.conn_handle, _HANDLE_READ_NAME)
        while self.read_done == False:
            pass
        self.read_done = False

    def getFirmwareVersion(self):
        self.connect()
        if self.connected == False:
            return 9
        self.__ble.gattc_read(self.conn_handle, _HANDLE_READ_VERSION)
        while self.read_done == False:
            pass
        self.read_done = False

    def getBatteryLevel(self):
        self.connect()
        if self.connected == False:
            return 9
        self.__ble.gattc_read(self.conn_handle, _HANDLE_READ_BATTERY)   
        while self.read_done == False:
            pass
        self.read_done = False

    def get_mitempdata(self):
        
        self.getBatteryLevel()
        self.getFirmwareVersion()
        self.getName()
        utime.sleep(1)
        self.getSensorData()
        return self.mitempdata

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
        gc.collect()

        res = {'result':9}        
        if cmnd == "getstatus":
            res = self.get_mitempdata()
            res["result"]=0
        if self.connected == True:
            self.disconnect()
        return res

def test_mithermometer():
    bt = BLE()
    bt.active(True)
    mithermometer = MiThermometer(bt,"4C:65:A8:DF:E9:37")
    print(mithermometer.get_mitempdata())
    


#test_mithermometer()    
#mithermometer.connect()
#mithermometer.getFirmwareVersion()
#mithermometer.getName()
#mithermometer.getSensorData()
#mithermometer.getBatteryLevel()

