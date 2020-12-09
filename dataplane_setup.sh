#!/bin/bash
#Author: Rahil Gandotra
#This script is used to setup the data plane infrastructure - install Mininet and initialize the custom topology used for GPF.

git clone git://github.com/mininet/mininet.git
cd mininet/
sudo apt-get update -y
util/install.sh -fnv
cd ..
echo Enter the controller IP:
read ctrlrIP
sudo mn --custom ./topo.py --topo mytopo --controller=remote,ip=$ctrlrIP --switch=ovsk,protocols=OpenFlow13 --mac
