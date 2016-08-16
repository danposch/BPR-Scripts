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

print "Deploying Code:"

# available pis: PREFIX.NR = IP
pi_list = range(PI_START_SUFFIX,PI_END_SUFFIX+1) # returns [start, ..., end-1]

print "Available PIs(" + str(len(pi_list)) + "): " + str(pi_list)

commands = {}
for i in pi_list:
	commands[MNG_PREFIX+str(i)] = []

	#change into ndn folder
	commands[MNG_PREFIX+str(i)].append("reboot")

for pi in commands:

	print "Rebooting Pi: " + pi
	s = ssh.Connection(pi, 'root', password = 'pi')
	s.execute("reboot")
	s.close()

print "Pis Rebooted!\n"
