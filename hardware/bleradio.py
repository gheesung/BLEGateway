from ubluetooth import BLE
            
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

class BLEClientDevice():
    '''
    Base class for all BLE devices
    All BLE Device inherit the property
    '''
    def __init__(self):
        self.ble_handle=None
        self.connected = False
    def peripheral_connect(self, data):
        print ("_IRQ_PERIPHERAL_CONNECT", data)
        conn_handle, addr_type, addr = data
        self.connected = True
        self.ble_handle= conn_handle
        self.addr_type = addr_type
        self.mac_addr = addr
    def peripheral_disconnect(self, data):
        print ("_IRQ_PERIPHERAL_DISCONNECT", data)
        conn_handle, addr_type, addr = data
        self.connected = False
        self.ble_handle= None

    def gattc_notify(self, data):
        print ("_IRQ_GATTC_NOTIFY", data)


class BLERadio():

    def __init__(self):
        self.ble_handle = BLE()
        self.ble_activated = False
        self.ble_devices={}

    def activate_ble(self):
        if self.ble_activated == False:
            self.ble_handle.active(False)
            print("Starting ble...")
            self.ble_handle.active(True)
            self.ble_activated = True
            self.ble_handle.config(rxbuf=256)
        return self.ble_handle
    
    def deactivate_ble(self):
        if self.ble_activated == True:
            self.ble_handle.active(False)
            self.ble_activated = False
    
    def add_device(self, bledevice):
        '''
        bledvice is of BLEDevice Object
        '''
        mac = bledevice["mac_addr"]
    
    def bt_irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            # A central has connected to this peripheral.
            conn_handle, addr_type, addr = data
        elif event == _IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            conn_handle, addr_type, addr = data
        elif event == _IRQ_GATTS_WRITE:
            # A central has written to this characteristic or descriptor.
            conn_handle, attr_handle = data
        elif event == _IRQ_GATTS_READ_REQUEST:
            # A central has issued a read. Note: this is a hard IRQ.
            # Return None to deny the read.
            # Note: This event is not supported on ESP32.
            conn_handle, attr_handle = data
        elif event == _IRQ_SCAN_RESULT:
            # A single scan result.
            addr_type, addr, adv_type, rssi, adv_data = data
        elif event == _IRQ_SCAN_DONE:
            # Scan duration finished or manually stopped.
            pass
        elif event == _IRQ_PERIPHERAL_CONNECT:
            # A successful gap_connect().
            conn_handle, addr_type, addr = data
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Connected peripheral has disconnected.
            conn_handle, addr_type, addr = data
        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # Called for each service found by gattc_discover_services().
            conn_handle, start_handle, end_handle, uuid = data
        elif event == _IRQ_GATTC_SERVICE_DONE:
            # Called once service discovery is complete.
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, status = data
        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            # Called for each characteristic found by gattc_discover_services().
            conn_handle, def_handle, value_handle, properties, uuid = data
        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            # Called once service discovery is complete.
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, status = data
        elif event == _IRQ_GATTC_DESCRIPTOR_RESULT:
            # Called for each descriptor found by gattc_discover_descriptors().
            conn_handle, dsc_handle, uuid = data
        elif event == _IRQ_GATTC_DESCRIPTOR_DONE:
            # Called once service discovery is complete.
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, status = data
        elif event == _IRQ_GATTC_READ_RESULT:
            # A gattc_read() has completed.
            conn_handle, value_handle, char_data = data
        elif event == _IRQ_GATTC_READ_DONE:
            # A gattc_read() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, value_handle, status = data
        elif event == _IRQ_GATTC_WRITE_DONE:
            # A gattc_write() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, value_handle, status = data
        elif event == _IRQ_GATTC_NOTIFY:
            # A peripheral has sent a notify request.
            conn_handle, value_handle, notify_data = data
        elif event == _IRQ_GATTC_INDICATE:
            # A peripheral has sent an indicate request.
            conn_handle, value_handle, notify_data = data


class iTAGBLE(BLEClientDevice):
    def __init__(self):
        super().__init__()