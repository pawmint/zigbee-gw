Zigbee Gateway
==============

This is the intern zigbee gateway program for ubigate. It each sensors present in the home and using zigbee communication protocol are using this gateway.

This program have to be set up on the beaglebone when sensors using zigbee are installed in a home.

##How To configure the BeagleBone:
Clone the git repository for zigbe-gw in /home and switch to the branch bedproto.

Create a virtual environment.

Install zigbee-gw and its dependencies:
```
~# python setup.py install
```

Adapt the config file:
```
~# cp resources/conf.ini.default resources/conf.ini
~# nano ressources/conf.ini
```

* Server and port correspond to the IP address and the listening port of your MQTT broker.
* Gateway and house correspond of the BeagleBone name and the house ID.

##How to run the program
*(If the BeagleBone is up to date)*

* Run the virtual environment

  ```
  ~# source <NameOfTheEnvironment>/bin/activate
  ```
* Run the MQTT broker.
* In the folder zigbee-gw run the software with the command:

  ```
  ~# python zigbee-gw.py
  ```
