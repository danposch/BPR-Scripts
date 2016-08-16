#@author dposch

import os
import paramiko
import ssh_lib as ssh
import node_parser as np

MNG_PREFIX = "192.168.0."
EMU_PREFIX = "192.168.1."
ITEC_GATEWAY = "10.0.0.1" # todo change this once router is setup

PI_START_SUFFIX = 10
PI_END_SUFFIX = 29

DEPLOY_MODE = "DEBUG"

print "Deploying Code:"

# available pis: PREFIX.NR = IP
pi_list = range(PI_START_SUFFIX,PI_END_SUFFIX+1) # returns [start, ..., end-1]

print "Available PIs(" + str(len(pi_list)) + "): " + str(pi_list)

commands = {}
for i in pi_list:
	commands[MNG_PREFIX+str(i)] = []

	#change into ndn folder
	commands[MNG_PREFIX+str(i)].append("cd ~/ndn")

	#update itec-NFD
	commands[MNG_PREFIX+str(i)].append("cd NFD")
	commands[MNG_PREFIX+str(i)].append("git pull")
	commands[MNG_PREFIX+str(i)].append("./waf")
	commands[MNG_PREFIX+str(i)].append("sudo ./waf install")
	commands[MNG_PREFIX+str(i)].append("cd ..")

	#checkout ndn-apps
	commands[MNG_PREFIX+str(i)].append("git clone https://github.com/danposch/ndn-apps.git")
	commands[MNG_PREFIX+str(i)].append("cd ndn-apps")
	commands[MNG_PREFIX+str(i)].append("git pull")
	commands[MNG_PREFIX+str(i)].append("./waf")
	commands[MNG_PREFIX+str(i)].append("sudo ./waf install")
	commands[MNG_PREFIX+str(i)].append("cd ..")

	#checkout and build libdash
	commands[MNG_PREFIX+str(i)].append("git clone https://github.com/bitmovin/libdash.git")
	commands[MNG_PREFIX+str(i)].append("cd libdash/")
	commands[MNG_PREFIX+str(i)].append("git pull")
	commands[MNG_PREFIX+str(i)].append("cd libdash/")
	commands[MNG_PREFIX+str(i)].append("mkdir build")
	commands[MNG_PREFIX+str(i)].append("cd build")
	commands[MNG_PREFIX+str(i)].append("cmake ../")
	commands[MNG_PREFIX+str(i)].append("make")
	commands[MNG_PREFIX+str(i)].append("cd ../../../")
	commands[MNG_PREFIX+str(i)].append("sudo cp ./libdash/libdash/build/bin/libdash.so  /usr/lib/")
	commands[MNG_PREFIX+str(i)].append("sudo mkdir /usr/include/libdash")
	commands[MNG_PREFIX+str(i)].append("sudo cp -r ./libdash/libdash/libdash/include/* /usr/include/libdash/")

	#checkout and build ndn-demo apps
	commands[MNG_PREFIX+str(i)].append("git clone https://github.com/theuerse/ndn-DemoApps.git")
	commands[MNG_PREFIX+str(i)].append("cd ndn-DemoApps/")
	commands[MNG_PREFIX+str(i)].append("git pull")
	commands[MNG_PREFIX+str(i)].append("./waf configure")
	commands[MNG_PREFIX+str(i)].append("./waf")
	commands[MNG_PREFIX+str(i)].append("sudo ./waf install")
	commands[MNG_PREFIX+str(i)].append("cd ..")

for pi in commands:

	#if pi != "192.168.0.13":
		#continue

	f = open(os.getenv("HOME")+"/deploy_code.sh",'w')
	f.write('#!/bin/sh\n') # python will convert \n to os.linesep

	print "Deploying Code to PI: " + pi
	for c in commands[pi]:
		#print c
		f.write(c+"\n")
	print

	f.close()

	s = ssh.Connection(pi, 'nfd', password = 'nfd')
	s.put(os.getenv("HOME")+"/deploy_code.sh", '/home/nfd/deploy_code.sh')
	s.execute("chmod +x /home/nfd/deploy_code.sh")
	s.execute("screen -d -m /home/nfd/deploy_code.sh")
	s.close()

print "Code deployed on PIs!\n"
