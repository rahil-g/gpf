#Author: Rahil Gandotra
#This file consists of the custom Mininet topology used for GPF.

from mininet.topo import Topo

class MyTopo(Topo):
    def __init__(self):

        Topo.__init__(self)

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1', listenPort=6675, dpid='0000000000000100')
        s5 = self.addSwitch('s5', listenPort=6676, dpid='0000000000000200')
        s2 = self.addSwitch('s2', listenPort=6677, dpid='0000000000000300')
        s3 = self.addSwitch('s3', listenPort=6678, dpid='0000000000000400')
        s4 = self.addSwitch('s4', listenPort=6679, dpid='0000000000000500')

        self.addLink(h1, s1)
        self.addLink(h2, s5)
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s1, s4)
        self.addLink(s5, s2)
        self.addLink(s5, s3)
        self.addLink(s5, s4)

topos = { 'mytopo': ( lambda: MyTopo() ) }
