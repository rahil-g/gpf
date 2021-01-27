#!/bin/bash
#Author: Rahil Gandotra
#This script is used to setup the control plane infrastructure - install RYU SDN controller and initialize the rest_router app used for GPF.

sudo apt-get update -y
sudo apt-get install python3-pip -y
git clone https://github.com/faucetsdn/ryu.git
cd ryu/
pip3 install .
sudo apt-get install python3-ryu -y
ryu run ryu/app/rest_router.py
