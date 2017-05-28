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


Installation instructions : 

1- WIFI configuration

from https://pimylifeup.com/raspberry-pi-wireless-access-point/ : 

Setting up the Wireless Access Point
As with most tutorials I do, this one just uses a clean version of Raspbian that has been updated to the latest packages.
To setup the Raspberry Pi wireless access point we will be making the use of two packages. These two packages are hostapd and dnsmasq. hostapd is the package that allows us to utilize a Wi-Fi device as an access point, in our case we will be utilizing this to turn the Raspberry Pi 3’s Wi-Fi into our access point.
The other package, dnsmasq acts as both a DHCP and DNS server so that we can assign IP addresses and process DNS requests through our Raspberry Pi itself. As a bonus dnsmasq is very easy to configure while being somewhat lightweight in comparison to isc-dhcp-server and bind9 packages.
Remember for this specific Raspberry Pi tutorial we will need to be utilizing an ethernet network connection and not the Wi-Fi connection.

1. Before we get started installing and setting up our packages, we will first run an update on the Raspberry Pi by running the following two commands.
sudo apt-get update
sudo apt-get upgrade

2. With that done we can now install our two packages, run the following to commands to install hostapd and dnsmasq.
sudo apt-get install hostapd
sudo apt-get install dnsmasq

3. With the packages now installed we will want to deny any interfaces from using our wlan0 connection, this will help ensure it is free for our access point. To do this we need to edit our dhcpd configuration file with the following command:
sudo nano /etc/dhcpcd.conf

4. Within this file we need to add the following line to the bottom. However, if you have any interfaces there, then make sure you place it above those as it is needed to override them.
denyinterfaces wlan0

Now we can save and quit out of the file by pressing Ctrl +X then pressing Y and then Enter.

5. Now we need to setup and configure our static IP address for the wlan0 connection, we will do this within our interfaces file. Begin editing this file by running the following command:
sudo nano /etc/network/interfaces

6. Within this file change the wlan0 section so it looks like below, this will setup the static ip address and allow hot plugging on the wlan0 connection.

allow-hotplug wlan0  
iface wlan0 inet static  
    address 192.168.220.1
    netmask 255.255.255.0
    network 192.168.220.0
    broadcast 192.168.220.255
#    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

Now we can save and quit out of the file by pressing Ctrl +X then Y and then Enter.

7. Now we need to restart our dhcpd service so it will load in all our configuration changes, we also need to reload our wlan0 interface to make sure it’s loaded in our interface changes. Run the following two commands to reload both:
sudo service dhcpcd restart
sudo ifdown wlan0; sudo ifup wlan0

8. Next, we need to adjust our hostapd configuration, to do this we need to begin editing the config file with the following command:
sudo nano /etc/hostapd/hostapd.conf

9. In this file we need to write out the following lines, these basically set up how we want to interact with the wlan device. The only real lines you should worry about in this file is the ssid= line and the wpa_passphrase= line.
NOTE: If you are doing this tutorial with a different Wi-Fi device then the inbuilt Pi 3 one, you may have to also change the driver= line to the best driver for your device, google will be your friend for working out what the best driver to use is.
interface=wlan0
driver=nl80211

hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
macaddr_acl=0
ignore_broadcast_ssid=0

# Use WPA2
auth_algs=1
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP

# This is the name of the network
ssid=Pi3-AP
# The network passphrase
wpa_passphrase=raspberry

Remember to change wpa_passphrase to your own password, make sure you set it to something secure so random people can’t just connect into your Wi-Fi access point.
Now we can save and quit out of the file by pressing Ctrl +X then pressing Y and then Enter.

10. With that done we should now have our hostapd configuration, but before it can be used we need to edit two files. These files are what hostapd will read to find our new configuration file.
To begin editing the first of these two files run the following command:
sudo nano /etc/default/hostapd

11. In this file, we need to find the following line and replace it:
Find:
#DAEMON_CONF="" 
Replace with:
DAEMON_CONF="/etc/hostapd/hostapd.conf"

Now we can save and quit out of the file by pressing Ctrl +X then pressing Y and then Enter.

12. Now we need to edit the second configuration file, this file is located within the init.d folder. We can edit the file with the following command:
sudo nano /etc/init.d/hostapd

13. In this file, we need to find the following line and replace it:
Find:
DAEMON_CONF= 
Replace with:
DAEMON_CONF=/etc/hostapd/hostapd.conf
Now we can save and quit out of the file by pressing Ctrl +X then pressing Y and then Enter.

14. With hostapd now set up we need to move onto setting up dnsmasq, before we begin editing its configuration we will move the default one to a new location. We can do this with the following command:
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

15. Now that the original configuration file is moved out of the way we can begin by creating our own new configuration file. We will create and edit the new file with the following command:
sudo nano /etc/dnsmasq.conf

16. To this file add the following lines, these lines basically tell the dnsmasq service how to handle all the connections coming through.
interface=wlan0       # Use interface wlan0  
listen-address=192.168.220.1   # Specify the address to listen on  
bind-interfaces      # Bind to the interface
server=8.8.8.8       # Use Google DNS  
domain-needed        # Don't forward short names  
bogus-priv           # Drop the non-routed address spaces.  
dhcp-range=192.168.220.50,192.168.220.150,12h # IP range and lease time  

Now we can save and quit out of the file by pressing Ctrl +X then pressing Y and then Enter.

17. Next, we need to configure your Raspberry Pi so that it will forward all traffic from our wlan0 connection over to our ethernet connection. First we must enable it through the sysctl.conf configuration file, so let’s begin editing it with the following command:
sudo nano /etc/sysctl.conf

18. Within this file you need to find the following line, and remove the # from the beginning of it.
Find:
#net.ipv4.ip_forward=1
Replace with:
net.ipv4.ip_forward=1

19. Now since we are impatient and don’t want to wait for it to enable on next boot we can run the following command to activate it immediately:
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

20. With IPv4 Forwarding now enabled we can configure a NAT between our wlan0 interface and our eth0 interface. Basically, this will forward all traffic from our access point over to our ethernet connection.
Run the following commands to add our new rules to the iptable:
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE  
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT  
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT  

21. Of course iptables are flushed on every boot of the Raspberry Pi so we will need to save our new rules somewhere so they are loaded back in on every boot.
To save our new set of rules run the following command:
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

22. Now with our new rules safely saved somewhere we need to make this file be loaded back in on every reboot. The most simple way to handle this is to modify the rc.local file.
Run the following command to begin editing the file:
sudo nano /etc/rc.local

23. Now we are in this file, we need to add the line below. Make sure this line appears above exit 0. This line basically reads the settings out of our iptables.ipv4.nat file and loads them into the iptables.
Find:
exit 0
Add above “exit 0”:
iptables-restore < /etc/iptables.ipv4.nat
Now we can save and quit out of the file by pressing Ctrl +X then pressing Y and then Enter.

24. Finally all we need to do is start the two services and enable them in systemctl. Run the following two commands:
sudo service hostapd start
sudo service dnsmasq start

25. Now you should finally have a fully operational Raspberry Pi wireless access point, you can ensure this is working by using any of your wireless devices and connecting to your new access point using the SSID and WPA Passphrase that was set earlier on in the tutorial.
To ensure everything will run smoothly it's best to try rebooting now. This will ensure that everything will successfully re-enable when the Raspberry Pi is started back up. Run the following command to reboot the Raspberry Pi:
sudo reboot



2- Software stack installation

If Python is not install, select version 2.7

Install the following libraries and frameworks following the instructions on the following sites:

Flask :
http://flask.pocoo.org/docs/0.11/installation/

MongoDb :
http://andyfelong.com/2016/01/mongodb-3-0-9-binaries-for-raspberry-pi-2-jessie/

Flask-Socket.io
https://flask-socketio.readthedocs.io/en/latest/

Flask-Mongoengine
http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/


3- Sources

nfcpy : https://nfcpy.readthedocs.io/en/latest/
