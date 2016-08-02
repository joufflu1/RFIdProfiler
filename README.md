# RFIdProfiler

This is a small prototype which detect a NFC/RFId tag and display an associated profile in a web page. The profile imitate data retrieved from a complete information system.

The hardware used is the following :

- Raspberry pi 3
- PN532 classical card for tag detection linked to RPi using the UART


All this software is needed for an independent operation :

- hostapd and dnsmasq for RPi 3 WIFI configuration
- python 2.7 + python dev library
- virtualenv
- MongoDB for hosting the profiles
- Flask
- Flask mongo engine
- Flask socketio
- eventlet
- gevent
- gevent-websocket

Installation instruction : To Do

