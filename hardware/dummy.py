import utime
class DummyHardware():
    '''
    Dummy Device class

    This class performs the default actions when the derived class did not implement
    the override method
    '''
    def __init__(self) :
        
        self.tranport_handler = None
    
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
        