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

print "Gathering Temperatures:"

# available pis: PREFIX.NR = IP
pi_list = range(PI_START_SUFFIX,PI_END_SUFFIX+1) # returns [start, ..., end-1]

print "Available PIs(" + str(len(pi_list)) + "): " + str(pi_list)

commands = {}
for i in pi_list:
	commands[MNG_PREFIX+str(i)] = []


for pi in commands:

	out_str = "Pi: " + pi
	s = ssh.Connection(pi, 'root', password = 'pi')
	
	#print s.execute("soctemp | cut -b 1-8 --complement")
	#print s.execute("hddtemp /dev/sda")
	out_str += "\tCPU: "+ s.execute("soctemp | cut -b 1-8 --complement")[0].strip()
	out_str += "\tHDD: "+ s.execute("hddtemp /dev/sda")[0].strip()[-5:]
	out_str += " ("+ s.execute("hddtemp /dev/sda")[0].strip().split(":")[1] + ")"
	s.close()
	print out_str

print "Done!\n"
