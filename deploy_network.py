#@author dposch

import os
import paramiko
import ssh_lib as ssh
import node_parser as np
import logging
import apps as ap
from igraph import *
from allPaths import *
from start_apps import *
from apps import *
import time
import copy

PI_CONFIG_HZ = 100
LATENCY = 100 #queue length of tbf in ms

def getNextFibHops(paths):
	cost_dict = {}
	for path in paths:
		nextHop = path[1]

		if nextHop in cost_dict.keys():
			if len(path) < len(cost_dict[nextHop]):
				cost_dict[nextHop] = path
		else:
			cost_dict[nextHop] = path

	return cost_dict.values()


def deployNetwork(NETWORK, PATHS, PI_START_SUFFIX, PI_END_SUFFIX, FW_STRATEGIES, MNG_PREFIX, EMU_PREFIX, ITEC_GATEWAY):

	print "Deploying Network: " + NETWORK

	# available pis: PREFIX.NR = IP
	pi_list = range(PI_START_SUFFIX,PI_END_SUFFIX+1) # returns [start, ..., end-1]

	print "Available PIs(" + str(len(pi_list)) + "): " + str(pi_list)

	nodes, link_list, property_list = np.parseNetwork(NETWORK);

	if len(pi_list) < nodes:
		print "Error to less PIs available to deploy network!"
		exit(-1)

	#map ipdresses to nodes
	for link in link_list:
		link.ip1 = EMU_PREFIX+str(pi_list[int(link.n1)])
		link.ip2 = EMU_PREFIX+str(pi_list[int(link.n2)])

	for prop in property_list:
		prop.ip_client = EMU_PREFIX+str(pi_list[int(prop.client)])
		prop.ip_server = EMU_PREFIX+str(pi_list[int(prop.server)])


	#init commands per pi { pi:[c1,c2,...,cn]}
	commands = {}
	for i in pi_list:
		commands[MNG_PREFIX+str(i)] = []

		#drop everything
		commands[MNG_PREFIX+str(i)].append("sudo iptables --flush") #delete all old entries
		commands[MNG_PREFIX+str(i)].append("sudo iptables -P INPUT DROP")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -P FORWARD DROP")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -P OUTPUT DROP")

		#but allow all ip traffic from the mangement interface
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A INPUT -d " + MNG_PREFIX+str(i) + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A INPUT -s " + MNG_PREFIX+str(i) + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A FORWARD -d " + MNG_PREFIX+str(i) + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A FORWARD -s " + MNG_PREFIX+str(i) + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A OUTPUT -d " + MNG_PREFIX+str(i) + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A OUTPUT -s " + MNG_PREFIX+str(i) + " -j ACCEPT")

		#setup the itec gateway
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A INPUT -d " + ITEC_GATEWAY + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A INPUT -s " + ITEC_GATEWAY + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A FORWARD -d " + ITEC_GATEWAY + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A FORWARD -s " + ITEC_GATEWAY + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A OUTPUT -d " + ITEC_GATEWAY + " -j ACCEPT")
		commands[MNG_PREFIX+str(i)].append("sudo iptables -A OUTPUT -s " + ITEC_GATEWAY + " -j ACCEPT")

		#delete all old tc settings (default ceil = rate)
		commands[MNG_PREFIX+str(i)].append("sudo tc qdisc del dev eth0 root");
		commands[MNG_PREFIX+str(i)].append("sudo tc qdisc add dev eth0 root handle 1: htb default " + str(10))
		commands[MNG_PREFIX+str(i)].append("sudo tc class add dev eth0 parent 1: classid 1:"+ str(10) + " htb rate 100mbit")

	for link in link_list:

		#ip
		ip1 = link.ip1
		ip2 = link.ip2

		#node id
		n1 = link.n1
		n2 = link.n2

		#add connection between nodes ip1 and ip2
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo iptables -A INPUT -d " + ip1 + " -s " + ip2 +" -j ACCEPT")
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo iptables -A FORWARD -d " + ip1 + " -s " + ip2 + " -j ACCEPT")
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo iptables -A FORWARD -d " + ip2 + " -s " + ip1 + " -j ACCEPT")
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo iptables -A OUTPUT -s " + ip1 + " -d " + ip2 + " -j ACCEPT")

		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo iptables -A INPUT -d " + ip2 + " -s " + ip1 +" -j ACCEPT")
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo iptables -A FORWARD -d " + ip2 + " -s " + ip1 + " -j ACCEPT")
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo iptables -A FORWARD -d " + ip1 + " -s " + ip2 + " -j ACCEPT")
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo iptables -A OUTPUT -s " + ip2 + " -d " + ip1 + " -j ACCEPT")

		#example: http://askubuntu.com/questions/776/how-i-can-limit-download-upload-bandwidth
		#add tc classes for n1 (default ceil = rate)

		handle_offset = 11
		flowId1 = "1:" + str(handle_offset+int(n2)) #towards n1
		flowId2 = "1:" + str(handle_offset+nodes+1+int(n2)) #from n1
		#commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc class add dev eth0 parent 1: classid " + flowId1 + " htb rate " + str(link.bw_n2_to_n1) + "kbit")	#towards n1
		#commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc class add dev eth0 parent 1: classid " + flowId2 + " htb rate " + str(link.bw_n1_to_n2) + "kbit") #from n1
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc class add dev eth0 parent 1: classid " + flowId1 + " htb rate 100mbit")	#towards n1
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc class add dev eth0 parent 1: classid " + flowId2 + " htb rate 100mbit") #from n1


		#add tc filter for n1
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dst " + ip1 + " match ip src " + ip2 + " flowid " + flowId1)	#towards n1
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dst " + ip2 + " match ip src " + ip1 + " flowid " + flowId2)	#from n1

		#add tbf below htp for queue length
		# burst >= rate / CONFIG_HZ # rate is in kbits
		burst = float(link.bw_n2_to_n1 * 1000) / (PI_CONFIG_HZ * 8)
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc qdisc add dev eth0 parent " + flowId1 + " handle " + str(handle_offset+int(n2)) +
																												 ": tbf rate " + str(link.bw_n2_to_n1) + "kbit burst " + str(int(burst)) + " latency " + str(LATENCY) + "ms") #towards n1

		burst = float(link.bw_n1_to_n2 * 1000) / (PI_CONFIG_HZ * 8)
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc qdisc add dev eth0 parent " + flowId2 + " handle " + str(handle_offset+nodes+1+int(n2)) +
																												 ": tbf rate " + str(link.bw_n1_to_n2) + "kbit burst " + str(int(burst)) + " latency " + str(LATENCY) + "ms") #from n1
		#delay and loss for n1 to n2
		netman_handle = str(handle_offset+(nodes+1)*2+int(n2))
		commands[ip1.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc qdisc add dev eth0 parent " + str(handle_offset+nodes+1+int(n2)) + ":" + str(int(n2)+1) + " handle " + netman_handle + " netem delay " + str(link.delay_n1_to_n2) + "ms" +
		str(link.loss_n1_to_n2))
		#sudo tc qdisc add dev eth0 parent 33:1 handle 9999 netem delay 10ms


		#add tc classes for n2 (default ceil = rate)
		flowId1 = "1:" + str(handle_offset+int(n1)) #towards n2
		flowId2 = "1:" + str(handle_offset+nodes+1+int(n1)) #from n2
		#commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc class add dev eth0 parent 1: classid " + flowId1 + " htb rate " + str(link.bw_n1_to_n2) + "kbit")	#towards n2
		#commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc class add dev eth0 parent 1: classid " + flowId2 + " htb rate " + str(link.bw_n2_to_n1) + "kbit")	#from n2
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc class add dev eth0 parent 1: classid " + flowId1 + " htb rate 100mbit")	#towards n2
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc class add dev eth0 parent 1: classid " + flowId2 + " htb rate 100mbit")	#from n2

		#add tc filter for n2
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dst " + ip2 + " match ip src " + ip1 + " flowid " + flowId1)	#towards n2
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dst " + ip1 + " match ip src " + ip2 + " flowid " + flowId2)	#from n2

		#add tbf below htp for queue length
		# burst >= rate / CONFIG_HZ # rate is in kbits
		burst = float(link.bw_n1_to_n2 * 1000) / (PI_CONFIG_HZ * 8)
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc qdisc add dev eth0 parent " + flowId1 + " handle " + str(handle_offset+int(n1)) +
																												 ": tbf rate " + str(link.bw_n1_to_n2) + "kbit burst " + str(int(burst)) + " latency " + str(LATENCY) + "ms") #towards n2

		burst = float(link.bw_n2_to_n1 * 1000) / (PI_CONFIG_HZ * 8)
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc qdisc add dev eth0 parent " + flowId2 + " handle " + str(handle_offset+nodes+1+int(n1)) +
																												 ": tbf rate " + str(link.bw_n2_to_n1) + "kbit burst " + str(int(burst)) + " latency " + str(LATENCY) + "ms") #from n2

		#delay and loss for n2 to n1
		netman_handle = str(handle_offset+(nodes+1)*2+int(n1))
		commands[ip2.replace(EMU_PREFIX, MNG_PREFIX)].append("sudo tc qdisc add dev eth0 parent " + str(handle_offset+nodes+1+int(n1)) + ":" + str(int(n1)+1) + " handle " + netman_handle + " netem delay " + str(link.delay_n2_to_n1) + "ms" +
		str(link.loss_n2_to_n1))

	print "Configuring NFDs:"

	#restart NFD on all PIs
	for pi in pi_list:
		commands[MNG_PREFIX + str(pi)].append("sudo nfd-stop")
		commands[MNG_PREFIX + str(pi)].append("sleep 5")
		commands[MNG_PREFIX + str(pi)].append("sudo nfd-start")
		commands[MNG_PREFIX + str(pi)].append("sleep 5")

	#deploy ALL shortest routes

	#1. we need a graph to calc the shortest / all paths
	g = Graph()
	g = g.as_directed()

	for pi in pi_list:
		g.add_vertex(EMU_PREFIX+str(pi))
	#g.add_vertices(len(pi_list))

	for link in link_list:
		g.add_edges( [(int(link.n1),int(link.n2)), (int(link.n2), int(link.n1)) ])

	g.vs["label"] = g.vs["name"]
	layout = g.layout("kk")
	#plot(g, layout = layout)

	for pi_idx, pi in enumerate(pi_list):
		for to_idx, to in enumerate(pi_list[pi_idx+1:]):

			#print "Start calc for pi:" +str(pi)
			if PATHS == "shortest":
				paths = g.get_all_shortest_paths(pi-PI_START_SUFFIX, to-PI_START_SUFFIX)
			elif PATHS == "all":
				paths = find_all_paths(g, pi-PI_START_SUFFIX, to-PI_START_SUFFIX, maxlen = nodes)
			else:
				print "Invalid Path selection! Please choose \"all\" or \"shortest\"!"
				exit(-1)
			#print "found " + str(len(paths)) + " for pair (" + str(pi) + "," + str(to) + ")"

			#store reverse pahts for to -> pi
			reverse_paths = copy.deepcopy(paths)
			for path in reverse_paths:
				path.reverse()

			#first calc and add fib entries from pi -> to
			paths = getNextFibHops(paths)

			#install next hop and costs
			for path in paths:
				for fws in FW_STRATEGIES:
					commands[MNG_PREFIX+ str(pi)].append("sudo nfdc register /" + fws +"/"+ str(to-PI_START_SUFFIX) +" udp://" +EMU_PREFIX + str(path[1]+PI_START_SUFFIX) + " -c " + str(len(path)-1)) # /FW_STRATEGY/Node_ID/

			#now calc and add fib entries from to -> pi
			reverse_paths = getNextFibHops(reverse_paths)

			#install next hop and costs
			for path in reverse_paths:
				for fws in FW_STRATEGIES:
					commands[MNG_PREFIX+ str(to)].append("sudo nfdc register /" + fws +"/"+ str(pi-PI_START_SUFFIX) +" udp://" +EMU_PREFIX + str(path[1]+PI_START_SUFFIX) + " -c " + str(len(path)-1)) # /

	#install strategies per fw-prefix on each pi
	for pi in pi_list:
		for fws in FW_STRATEGIES:
			commands[MNG_PREFIX+ str(pi)].append("sudo nfdc set-strategy " + "/"+fws + "/ /localhost/nfd/strategy/" + fws) #set-strategy <namespace> <strategy-name>

	#print commands

	#logging.basicConfig(level=logging.DEBUG)

	apps = {}
	for prop in property_list:
		#add client app
		if prop.ip_client in apps.keys():
			"Configuration Error! Only one Client-App per Node!"
			exit(-1)

		apps[prop.ip_client.replace(EMU_PREFIX, MNG_PREFIX)] = []
		#apps[prop.ip_client.replace(EMU_PREFIX, MNG_PREFIX)].append("sleep 10") #Clients Sleep so Servers can Start first..# Not anymore nessecary
		apps[prop.ip_client.replace(EMU_PREFIX, MNG_PREFIX)].append(ap.getConsumerCommand(prop.client, prop.server))

		#add server app
		if prop.ip_server in apps.keys():
			continue #servers may appear in multiple properties as 1 server may serve for many clients

		apps[prop.ip_server.replace(EMU_PREFIX, MNG_PREFIX)] = []
		apps[prop.ip_server.replace(EMU_PREFIX, MNG_PREFIX)].append(ap.getProducerCommand(prop.server))

	#print
	#prepare client.sh for logging
	orig_f = open("client.sh", "r")
	modified_f = open (os.getenv("HOME")+"/client.sh",'w')
	modified_f.write('#!/bin/sh\n');

	for line in orig_f:
		modified_f.write(line.replace("$$$TRACKAPP$$$", getTrackApp()))
	modified_f.close()
	orig_f.close()

	#deploy network
	for pi in commands:

		print "Setting up Network Settings for PI: " + pi

		with open(os.getenv("HOME")+"/network.sh",'w') as f:
			f.write('#!/bin/sh\n') # python will convert \n to os.linesep
			for c in commands[pi]:
				#print c
				f.write(c+"\n")
			f.close()

		#check if pi shall run an app

		hasApp = False
		if pi in apps.keys():

			hasApp = True
			print "Setting up App Script for PI: " + pi

			with open(os.getenv("HOME")+"/app.sh",'w') as f:
				f.write('#!/bin/sh\n') # python will convert \n to os.linesep
				for c in apps[pi]:
					#print c
					f.write(c+"\n")
				f.close()
		else:
			print "No Apps for this Pi."

		print "Pushing Settings and Apps to PI via SSH..."

		#open ssh
		s = ssh.Connection(pi, 'root', password = 'pi')

		#remove old scripts and log files
		s.execute("rm -f /home/nfd/network.sh")			#network settings
		s.execute("rm -f /home/nfd/app.sh")					#deployed app
		s.execute("rm -f /home/nfd/consumer-PI_*.log")	#app logs
		s.execute("rm -f /tmp/logs/*.json")					#pi-usage logs
		s.execute("rm -f /home/nfd/*.nfd-status.log")	#nfd-status logs

		#create pi-usage log folder if it does not exists...
		s.execute("mkdir /tmp/logs")

		#copy new scripts
		s.put(os.getenv("HOME")+"/network.sh", '/home/nfd/network.sh')
		s.execute("chmod +x /home/nfd/network.sh")
		if hasApp:
			s.put(os.getenv("HOME")+"/app.sh", '/home/nfd/app.sh')
			s.execute("chmod +x /home/nfd/app.sh")

		s.put(os.getenv("HOME")+"/client.sh", "/root/client.sh")
		s.execute("chmod +x /root/client.sh")

		#launch nfd
		s.execute("screen -d -m /home/nfd/network.sh")
		s.close()
		print "Pi:" + pi + "	Done!\n"

	print "Network deployed on all PIs! Waiting 180 seconds so Pis can startup NFD and set routes!\n"
	time.sleep(120)
	return g, pi_list, property_list
