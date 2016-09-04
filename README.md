# RFIdProfiler

This is a small prototype which detect a NFC/RFId tag and display an associated profile in a web page. 
The profile imitate data retrieved from a complete information system.

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

Installation instruction : 


1- WIFI configuration

Make sure the Ethernet cable is connected in and you can ping out from the Pi

In Terminal, check with ifconfig -a command if you see wlan0 interface.

Next, install the software on the Pi3 that will act as the host access point :

> sudo apt-get update
> sudo apt-get install hostapd dnsmasq


1.1- After the installation, set the DHCP server by configuring dnsmasq :

The configuration is done in dnsmasq.conf file, execute the followong commands :

> sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig  
> sudo vi /etc/dnsmasq.conf

and paste the following lines :

interface=wlan0      # Use interface wlan0  
listen-address=127.0.0.1 # Explicitly specify the address to listen on  
bind-interfaces      # Bind to the interface to make sure we aren't sending things elsewhere  
server=8.8.8.8       # Forward DNS requests to Google DNS  
domain-needed        # Don't forward short names  
bogus-priv           # Never forward addresses in the non-routed address spaces.  
dhcp-range=192.168.42.10,192.168.42.150,12h # Assign IP addresses between 172.24.1.50 and 172.24.1.150 with a 12 hour lease time


1.2- Set up wlan0 interfce for static IP

First run :

> sudo ifdown wlan0

> sudo vi /etc/network/interfaces 

Find the line auto wlan0 and add a # in front of the line, and in front of every line afterwards. If you don't have that line, just make sure it looks like the screenshot below in the end! Basically just remove any old wlan0 configuration settings, we'll be changing them up Depending on your existing setup/distribution there might be more or less text and it may vary a little bit
Add the lines
	1. iface wlan0 inet static
	2.  address 192.168.42.1
	3.  netmask 255.255.255.0
After allow-hotplug wlan0

Assign a static IP address to the wifi adapter by running : 

> sudo ifconfig wlan0 192.168.42.1


1.3- Configure the access point

Create a new file by running :
> sudo vi /etc/hostapd/hostapd.conf

Paste the folowing lines : (change the passphrase by your own password, for RPi3 the driver is nl80211 but it may change using a WIFI dongle)

interface=wlan0
driver=nl80211
ssid=Pi_AP
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=Raspberry
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP

Save as usual. Make sure each line has no extra spaces or tabs at the end or beginning

Tell the Pi where to find this configuration file. Run : 
> sudo vi /etc/default/hostapd

Find the line #DAEMON_CONF="" and edit it so it says 
DAEMON_CONF="/etc/hostapd/hostapd.conf"
(Don't forget to remove the # in front to activate it!)


1.4- Configure Network Adress Translation

Setting up NAT will allow multiple clients to connect to the WiFi and have all the data 'tunneled' through the single Ethernet IP.
(But you should do it even if only one client is going to connect)

> sudo vi /etc/sysctl.conf

Scroll to the bottom and add net.ipv4.ip_forward=1 
on a new line, then run for immediate activation: 

> sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

Run the following commands to create the network translation between the ethernet port eth0 and the wifi port wlan0 : 

	> sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
	> sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
    > sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT 

To make this happen on reboot run :
> sudo sh -c "iptables-save > /etc/iptables.ipv4.nat" 

run :  
> sudo vi /etc/network/interfaces and add 
up iptables-restore < /etc/iptables.ipv4.nat
at the end of the file

Configuration is finished, to test it immediately without rebooting run :

sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf

You can try connecting and disconnecting from the Pi_AP with the password you set before (probably Raspberry if you copied our hostapd config), 
debug text will display on the Pi console but you won't be able to connect through to the Ethernet connection yet. 


1.5- Set a daemon to run everything at startup

> sudo service hostapd start
> sudo service isc-dhcp-server start

To start the daemon services. Verify that they both start successfully (no 'failure' or 'errors')

Then to make it so it runs every time on boot :

> sudo update-rc.d hostapd enable 
> sudo update-rc.d isc-dhcp-server enable 


