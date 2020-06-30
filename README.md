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

Only 1 transport handler is supported at 1 time.




# References
https://github.com/fizista/micropython-umqtt.simple2
https://github.com/RoButton/switchbotpy
