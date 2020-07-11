from ubluetooth import BLE
            
class BLERadio():

    def __init__(self):
        self.ble_handle = BLE()
        self.ble_activated = False

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
    