#Author: Rahil Gandotra
#This script is the implementation of GPF's network knob using the SDN-Controllers and Mininet VM's.
#Three knob modes are implemented-
#Mode 1: Forwarding decisions are based on energy efficiency only; network performance parameters is not considered.
#Mode 2 (default): Forwarding decisions are based on both energy efficiency and network performance parameters.
#Mode 3: Forwarding decisions are based on network performance parameters only; energy efficiency is not considered.

import requests, csv, time, ipaddress, copy, re
from netaddr import IPNetwork

ctrl_IP = input('Enter the controller IP: ')
contlr_rest_endpoint = 'http://'+ctrl_IP+':8080/router/'

netpow_IP = input('Enter the IP on which the NetPow app is accessible: ')
netpow_rest_endpoint = 'http://'+netpow_IP+':5002/devices/'

devices = []
routing_table = {}
ee = {'0000000000000064': 0.1, '0000000000000128': 0.1}
nw_dpids = []
nw_ips = {}
nw_nexthops = {}
nw_nws = []
dev_pwr_traff = {}
dev_max_mbps = {}
dev_route_ids = {}

def knob_mode():
    knob = input('Please select knob mode 1/2/3 (default: 2):\n1. Forwarding decisions are based on energy efficiency only; network performance parameters are not considered.\n2. Forwarding decisions are based on both energy efficiency and network performance parameters. (default)\n3. Forwarding decisions are based on network performance parameters only; energy efficiency is not considered.\n')
    if knob:
        knob = int(knob)
    
    if knob == '':
        knob = 2
    
    if (knob > 3) or (knob < 1):
        knob = input('Wrong input! Please select from modes 1, 2, or 3: ')
        if not knob:
            knob = 2

    return(knob)

knob = knob_mode()
print('Knob mode selected:',str(knob))

def rest_fetch_initial(dpid, mip, mport):
    uri = mip+':'+mport
    url = netpow_rest_endpoint + uri
    r = requests.get(url)
    pwr = r.text.split(',')[2]
    pwr = pwr.replace('\"','')
    pwr = float(pwr)
    traffic = r.text.split(',')[5]
    traffic = traffic.replace('\"','')
    traffic = float(traffic)
    delay = r.text.split(',')[6]
    delay = delay.replace('\"','')
    delay = float(delay)
    loss = r.text.split(',')[7]
    loss = loss.replace('\"','')
    loss = loss.replace(']','')
    loss = float(loss)
    templist = []
    templist.append(pwr)
    templist.append(traffic)
    templist.append(delay)
    templist.append(loss)
    dev_pwr_traff[dpid] = templist
    dev_max_mbps[dpid] = traffic
    if knob == 1:
        c1 = 1
        c2 = c3 = c4 = 0
    elif knob == 2:
        c1 = 0.75
        c2 = c3 = c4 = 0.25
    elif knob == 3:
        c1 = 0
        c2 = c3 = c4 = 1
    return((c1 * pwr) + ((c2 * 10000) / traffic) + (c3 * delay) + (c4 * loss))

def discover(fname):
    print('Reading the NSOT file...')
    time.sleep(2)
    with open(fname) as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                if str(row[0]) != 'DPID':
                    iplist = []
                    for ip in row[3].split(', '):
                        iplist.append(ip)
                    devices.append({'dpid':str(row[0].zfill(16)), 'mgmtIP':str(row[1]), 'mgmtPort':str(row[2]), 'IPassign':iplist})
                    nw_dpids.append(str(row[0].zfill(16)))
                    nw_ips[str(row[0].zfill(16))] = iplist
                    if str(row[2]) != '1029' and str(row[2]) != '1030':
                        ee[str(row[0].zfill(16))] = rest_fetch_initial(str(row[0].zfill(16)), str(row[1]), str(row[2]))
                    nw_dict = {}
                    for nw in iplist:
                        route = []
                        route.append(ee[str(row[0].zfill(16))])
                        route.append('xx')
                        nw_addr = ipaddress.IPv4Network(nw, strict=False).exploded
                        nw_dict[str(nw_addr)] = route
                        if str(nw_addr) not in nw_nws:
                            nw_nws.append(str(nw_addr))
                    dev_dict = {}
                    dev_dict[str(row[0].zfill(16))] = nw_dict
                    routing_table[str(row[0].zfill(16))] = nw_dict
                    
discover('NSOT - Knob.csv')
#print(devices)
print(len(devices),'devices discovered.')

print('Fetching initial power, bandwidth, delay, and loss values...')
time.sleep(1)

print('Computing routing metrics according to knob value set...')

print('Computing initial routing table...')
time.sleep(2)

print('Determining network topology...')
time.sleep(2)
links = {}
for d in routing_table:
    for e in routing_table:
        if d != e:
            if (d,e) and (e,d) not in links:
                for i in routing_table[d]:
                    for j in routing_table[e]:
                        if i == j:
                            if int(d) <= int(e):
                                links[d,e] = 1
                            else:
                                links[e,d] = 1

def next_hops(nw_ips):
    for d in nw_ips:
        next_hop = {}
        for e in nw_ips:
            if d != e:
                for i in nw_ips[d]:
                    for j in nw_ips[e]:
                        if IPNetwork(i) == IPNetwork(j):
                            next_hop[e] = j.split('/')[0]
        nw_nexthops[d] = next_hop

next_hops(nw_ips)

def assignIP(device):
    dpid = device['dpid']
    ip_addresses = device['IPassign']
    url = contlr_rest_endpoint + dpid
    for ip in ip_addresses:
        address = '{\"address\":\"'+ip+'\"}'
        r = requests.post(url, data = address)
        print(url,address,r.text)
        time.sleep(0.25)

print('Assigning IP addresses to devices\' interfaces...')
time.sleep(2)
for d in devices:
    assignIP(d)

def GPF(devices,temp_rt):
    for l in nw_dpids:
        q = []
        for n in nw_dpids:
            q.append(n)
        s = []
        while len(q) != 0:
            for i in nw_dpids:
                while i not in s:
                    q.remove(i)
                    s.append(i)
                    neigh = 0
                    for y,z in links:
                        if (l == y and i == z) or (l == z and i == y):
                            neigh = 1
                    if neigh != 0:
                        if l == '0000000000000128' and i == '0000000000000064':
                            print('yes')
                        for rou in temp_rt[i]:
                            if rou in temp_rt[l]:
                                if temp_rt[l][rou][1] != 'xx':
                                    if temp_rt[l][rou][0] > temp_rt[i][rou][0] + ee[l]:
                                        temp_rt[l][rou][0] = temp_rt[i][rou][0] + ee[l]
                                        temp_rt[l][rou][1] = i
                            else:
                                rlist = []
                                rlist.append(temp_rt[i][rou][0] + ee[l])
                                rlist.append(i)
                                temp_rt[l][rou] = rlist
    return(temp_rt)

temp_rt = {}
temp_rt = copy.deepcopy(routing_table)
print('\nRunning GPF...')
temp_rt = GPF(devices,temp_rt)
time.sleep(1)
temp_rt = GPF(devices,temp_rt)

for d in temp_rt:
    if len(temp_rt[d]) != len(nw_nws):
        GPF(devices,temp_rt)
        time.sleep(1)

def assign_routes(routing_table,nw_nexthops):
    for d in routing_table:
        templist = []
        for n in routing_table[d]:
            if routing_table[d][n][1] != 'xx':
                url = contlr_rest_endpoint + d
                data = '{\"destination\": \"'+n+'\", \"gateway\": \"'+nw_nexthops[d][routing_table[d][n][1]]+'\"}'
                r = requests.post(url, data = data)
                print(url,data,r.text)
                m = re.search('route_id=\d+',r.text)
                rid = m.group(0)
                rid = rid.replace('route_id=','')
                templist.append(rid)
                time.sleep(0.2)
        dev_route_ids[d] = templist

print('GPF algorithm run complete. Pushing static routes...')
assign_routes(temp_rt,nw_nexthops)

print('\nAll done, please test :)\n')

def rest_fetch():
    for d in devices:
        if d['mgmtPort'] != '1029' and d['mgmtPort'] !='1030':
            uri = d['mgmtIP']+':'+d['mgmtPort']
            url = netpow_rest_endpoint + uri
            r = requests.get(url)
            pwr = r.text.split(',')[2]
            pwr = pwr.replace('\"','')
            pwr = float(pwr)
            traffic = r.text.split(',')[5]
            traffic = traffic.replace('\"','')
            traffic = float(traffic)
            delay = r.text.split(',')[6]
            delay = delay.replace('\"','')
            delay = float(delay)
            loss = r.text.split(',')[7]
            loss = loss.replace('\"','')
            loss = loss.replace(']','')
            loss = float(loss)
            templist = []
            templist.append(pwr)
            templist.append(traffic)
            templist.append(delay)
            templist.append(loss)
            dev_pwr_traff[d['dpid']] = templist

def ee_calculator():
    for p,t in dev_pwr_traff.items():
        curr_W = t[0]
        curr_Mbps = t[1]
        curr_delay = t[2]
        curr_loss = t[3]
        if knob == 1:
            c1 = 1
            c2 = c3 = c4 = 0
        elif knob == 2:
            c1 = 0.75
            c2 = c3 = c4 = 0.25
        elif knob == 3:
            c1 = 0
            c2 = c3 = c4 = 1
        ee[p] = ((c1 * curr_W) + ((c2 * 10000) / curr_Mbps) + (c3 * curr_delay) + (c4 * curr_loss))

def del_routes(dev_route_ids):
    for d,l in dev_route_ids.items():
        templist = []
        for r in l:
            url = contlr_rest_endpoint + d
            data = "{\"route_id\": "+str(r)+"}"
            req = requests.delete(url, data = data)
            print(url,data,req.text)
            time.sleep(0.1)
            templist.append(r)
        for ro in templist:
            l.remove(ro)

while True:
    knob = knob_mode()
    print('Knob mode selected:',str(knob))
    del_routes(dev_route_ids)
    print('Fetching current power, bandwidth, delay, and loss values...')
    rest_fetch()
    time.sleep(1)
    print('Computing routing metrics according to knob value set...')
    ee_calculator()
    time.sleep(1)
    print('Running GPF...')
    temp_rt = {}
    temp_rt = copy.deepcopy(routing_table)
    temp_rt = GPF(devices,temp_rt)
    time.sleep(1)
    temp_rt = GPF(devices,temp_rt)
    time.sleep(1)
    temp_rt = GPF(devices,temp_rt)
    print('Deleting old routes...')
    time.sleep(1)
    print('Pushing static routes...')
    assign_routes(temp_rt,nw_nexthops)
    print('\nAll done, please test :)\n')