# Simplenet

Simple network creation for busy pentesters/sysamdins.

## Features

* Bond interfaces and creates a switch between them (to capture traffic without a tap or a hub)
* Connect to the virtual switch, get an IP (static, dhcp *not yet*)
* Nat the network created by the virtual switch
* Assign IP addresses on the subnet with DHCP *Not yet*
* Spins up a radius server *Not yet*

## Requirements

* python3
* docopts (python library)
* bridge-utils

## Examples

Network interfaces can be listed by using `ip l` or `ip a`.

### Intercept traffic on a link

I have two network interfaces : eth0 and eth1, I want to connect them and
capture the traffic :

```bash
./simplenet switch --name eavedrop eth0 eth1
```

Now a `tcpdump -i eavedrop` will almost look like  the output of a network tap.

### Chain laptops

I have two laptops but only one RJ45 port to the LAN. One of the laptops have
two interfaces : eth0 and eth1. My IP on the lan is 192.168.2.100 and the
subnet is 192.168.0.0/16.

```bash
./simplenet.py switch --name switch --with-ip --ip 192.168.2.1 --subnet 192.168.0.0/16 eth0 eth1
```

### Create a NATed LAN

The interface eth2 is connected to the WAN. Make sure you have an IP and a
default route.

```bash
./simplenet.py switch --name switch --with-ip --ip 192.168.2.1 --subnet 192.168.0.0/16 eth0 eth1
./simplenet.py nat switch eth2
```
