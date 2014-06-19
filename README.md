Zigbee Gateway
==============

This is the intern zigbee gateway program for ubigate. It each sensors present in the home and using zigbee communication protocol are using this gateway.

This program have to be set up on the beaglebone when sensors using zigbee are installed in a home.

##How To configure the BeagleBone:
Create a git repository for ubigate in /home switch to the branch API
Create the git repository for zigbe-gw in /home. switch to the branch dev
Create a virtual environment and install the following libraries:
```
argparse==1.2.1
mosquitto==1.2.3
pyserial==2.7
pytz==2014.4
tzlocal==1.1.1
wsgiref==0.1.2
```
Install ubigate in the virtual environment:
```
~# python /home/ubiGATE/setup.py develop
```
Adapt the config file:
```
edit the file /home/ressources/conf.ini
server and port correspond to the IP address and the listening port of your MQTT broker.
gateway and house correspond of the BeagleBone name and the house ID.
```

##How to run the program
(If the BeagleBone is up to date)

Run the proper virtual environment
```
In the root of the BeagleBone write the line
~#source <NameOfTheEnvironment>/bin/activate
```
Run the MQTT broker
Run the program
```
In the folder /home/zigbee-gw/ run the software with the command
~#python zigbee-gw.py
```
