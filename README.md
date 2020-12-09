# GPF - Green Power Forwarding
A novel technique for energy efficient network operations.

![GPF_Topo](https://github.com/rahil-g/gpf/blob/main/images/Picture1.png)

### Quick Start

Tested on OS: Ubuntu 16.04.07 LTS

Install GPF from the source code -
```
$ git clone https://github.com/rahil-g/gpf.git
$ cd gpf/
```

First, set up the data-plane infrastructure of Open vSwitches using -
```
$ bash dataplane_setup.sh
```
Next, inside the Mininet CLI, change the IP addresses and static routes of the hosts using -
```
mininet> source ipconf
```
