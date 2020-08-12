import utime
import uasyncio as asyncio

class BaseHardware():
    '''
    Base Hardware class

    All hardware must be derived from this class. It handles the default actions.
    Derived class can override the base class methods .
    '''
    
    def __init__(self, config) :
        self.config = config
        self.tranport_handler = None
        self.ble_handle = None

        self.loop = asyncio.get_event_loop()

        # ble - activate BLE if required
        if self.config["enable_ble"] == True:
            from hardware.bleradio import BLERadio
            bleradio = BLERadio()
            self.ble_handle = bleradio.activate_ble()
    
    def get_ble_handle(self):
        return self.ble_handle
    
    def get_async_loop(self):
        return self.loop
    
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
    
    def get_bat_voltage(self):
        return 0
    

    # start the coroutine for the transport object e.g. MQTT
    def start_transport(self):
        self.loop.create_task(self.tranport_handler.start())
        
    # The start the main loop
    def start(self):
        self.loop.run_until_complete(main_loop())

async def main_loop():
    while True:
        await asyncio.sleep(5)            