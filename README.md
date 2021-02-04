# GPF - Green Power Forwarding - Network Dial
A novel technique for energy efficient network operations.

The objective is to provide the capability to tradeoff between energy savings and network performance. Energy savings are achieved by prioritizing paths that consume less energy, while network performance is achieved by prioritizing paths having higher amounts of bandwidth, low latencies, and low packet losses. 

Three different network dial modes are defined -

**Mode 1:** Forwarding decisions are based on energy savings only; network performance parameters is not considered.

**Mode 2 (default):** Forwarding decisions are based on both energy savings and network performance parameters.

**Mode 3:** Forwarding decisions are based on network performance parameters only; energy savings is not considered.

The implementation consists of running a GPF algorithm on the network controller that takes the energy consumption and network performance parameters as inputs from the [NetPow](https://github.com/rahil-g/netpow) app, also takes input of the network dial mode from the user, computes the paths accordingly, and reconfigures the network dynamically.

![GPF_Topo](https://github.com/rahil-g/gpf/blob/main/images/Picture1.png)

### Quick Start

Tested on OS: Ubuntu 18.04.5 LTS

Install GPF from the source code -
```
$ git clone https://github.com/rahil-g/gpf.git
$ cd gpf/
```

First, set up the data-plane infrastructure of Open vSwitches using -
```
$ bash dataplane_setup.sh
```
Inside the Mininet CLI, change the IP addresses and static routes of the hosts using -
```
mininet> source ipconf
```

Next, in another terminal, set up the control-plane infrastructure of Ryu SDN controller using -
```
$ bash controlplane_setup.sh
```



## To-do list:
* 

## Status
Project is: in progress.

## Contact
Created by [Rahil Gandotra](mailto:rahil.gandotra@colorado.edu) - feel free to contact me!
