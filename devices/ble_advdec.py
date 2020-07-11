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
        #if res["result"] == 0:
        #    self.display_result(res)
        return 
    
    def display_result(self, res):
        text = {}
        text["line1"] = self.deviceconfig["friendlyname"]
        text["line2"] = "Action: " + res["command"]
        if res["command"] == "alarm":
            text["line3"] = "Status: " + res["alarm"]
        elif res["command"] == "getstatus":
            text["line3"] = "Batt: " + str(res["battery"])
        self.hardware.display_result(text)