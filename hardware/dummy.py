import utime
class DummyHardware():
    '''
    Dummy Device class

    This class performs the default actions when the derived class did not implement
    the override method
    '''
    
    def __init__(self, config) :
        self.config = config
        self.tranport_handler = None
        self.ble_handle = None

        # ble - activate BLE if required
        if self.config["enable_ble"] == True:
            from hardware.bleradio import BLERadio
            bleradio = BLERadio()
            self.ble_handle = bleradio.activate_ble()
    
    def get_ble_handle(self):
        return self.ble_handle
    
    def set_transport_handler(self, transport_handler):
        self.tranport_handler = transport_handler
    
    def blink(self, totalblink=5):
        count=0
        while count < totalblink:
            print("Blinking On")
            utime.sleep(0.1)
            print("Blinking Off")
            utime.sleep(0.1)
            count +=1
        
    def show_setupcomplete(self):
        self.blink(10)
    
    def display_result(self, text):
        print("Display Result")