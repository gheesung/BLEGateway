from micropython import const
import utime
import gc
def decode_mac(addr):
    """
    Decode readable mac address 
    """
    assert isinstance(addr, bytes) and len(addr) == 6, ValueError("mac address value error")
    return ":".join(['%02X' % byte for byte in addr])


class Device():
    def __init__(self, hardware, deviceconfig):
        
        self.hardware = hardware
        self.deviceconfig = deviceconfig
        self.devicename = deviceconfig["devicename"]
    
    def handle_request(self, cmnd, data):
        '''
        This function is required because it handle all the 
        incoming command and action

        For SwitchBot, the commands 
        press  
            return : successful - {"status":0} 
                     error - {"status": 9}
        '''
        gc.collect()

        if cmnd == "decode_ad_data":
            print(data)
            self.display_result(data)
        return 
    
    def display_result(self, data):
        text = {}
        text["line1"] = data["friendlyname"]
        text["line2"] = "rssi: " + str(data["rssi"])
        text["line3"] = ""
        self.hardware.display_result(text)