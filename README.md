Zigbee Gateway
==============

Reads date from the sensors in the home using zigbee communication protocol, and transfers it to the server through MQTT, using the ubigate library.

This program has to be set up on the Raspberry Pi Gateway when sensors using zigbee are installed in a home.

Currently, it can only be used for the bed sensor.

## Config

Zigbee-gw reads config files from two distinct locations:

* $HOME/zigbee-gw/conf.json
* /etc/xdg/zigbee-gw/conf.json

Here is a template `conf.json`:

```
{
  "gateways": [
    {
      "name": "XXX-zigbee",
      "server": "normandie.ubismart.org",
      "port": 1883,
      "username": "normandie",
      "password": "normandie"
    }
  ],
  "houses": [
    {
      "id": "1",
      "name": "My_house",
      "prefix": "A",
      "sensors": [
        "BED-0",
      ]
    }
  ],
  "logging": {
    "file": "info",
    "stdout": "debug"
  },
  "device": "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A7026AAW-if00-port0"
  * OR *
  "device": "/dev/serial/by-id/usb-FTDI_XBIB-U-DEV-if00-port0"
}
```

## External files

* Event buffer: $HOME/.cache/zigbee-gw/<gateway-name>.json
* Log: $HOME/.cache/zigbee-gw/log/zigbee-gw.log
