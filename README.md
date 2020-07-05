# BLEGateway

BLEGateway is Micropython script that allows BLE devices to be controlled via MQTT. The writeup can be found at my [blog](https://iotdiary.blogspot.com/2020/06/micropython-ble-and-esp32-switchbot.html) to describe the details of handling the BLE devices.

### BLE Block Diagram



## Setup and Configuration
This script will only work with Micropython unstable build from 2020-06-10 onwards. The older version BLE constants are not compatible with the current code.
### Configure config.json

1. Rename the config.sample.json to config.json.
2. Sample of the config.json

```json
{
    "transport" : "mqtt",
    "hardware" : "m5stack_core",
    "mqtt" : {
        "wifi_ssid": "SSID",
        "wifi_pw" : "PASSWORD",
        "mqtt_server" : "xx.xx.xx.xx",
        "mqtt_port" : 1883,
        "mqtt_clientid" : "blegateway_01",
        "userid": "",
        "password":"",
        "topicprefix": "bs/studyrm/ble/"
    },
    "devices" : [
        {
            "devicename": "studyrmfan",
            "devicetype": "switchbot",
            "deviceprotocol" : "ble",
            "mac" : "C6:23:6C:64:20:C1"
        },
        {
            "devicename": "studyrm02",
            "devicetype": "switchbot",
            "deviceprotocol" : "ble",
            "mac" : "F8:AB:2C:3E:DE:9B"
        }
    ]
}
```
## Concepts
This gateway consists of 3 major components:
1. transport
2. hardware
3. device

"transport" - This object take care of listening to external requests, activates the right device to get the information and returns the results to the requester. Only 1 transport handler is supported at 1 time and currently the only transport handler is MQTT.

"hardware" - This object specify the micro controller whereby this module operates on. e.g. M5Stack Core. This object implements the avaialble hardwares like the ili9341 screen, buttons etc. 

"device" - This object specifies the sensor(s) or actuator(s) to operate on. e.g. Xiaomi Temperature and Humidity sensor. The sensor(s) or actuator(s) can be internal or external to the hardware. It is specified as "device" so that it can be controlled externally by other systems.






# References
https://github.com/fizista/micropython-umqtt.simple2
https://github.com/RoButton/switchbotpy
https://github.com/rdagger/micropython-ili9341

