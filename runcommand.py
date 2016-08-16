#@author dposch

import os
import sys
import paramiko
import ssh_lib as ssh
import node_parser as np

MNG_PREFIX = "192.168.0."
EMU_PREFIX = "192.168.1."

PI_START_SUFFIX = 10
PI_END_SUFFIX = 29

print "Running command:"

SRC_FILE = ""
DEST_FILE = ""
USER = ""
PASSWD = ""

if len(sys.argv) != 4:
	print "Invalid Parameters -- Usage:"
	print "script, user, passwd"
	exit(-1)

cmd = str(sys.argv[1])
USER = str(sys.argv[2])
PASSWD = str(sys.argv[3])

# available pis: PREFIX.NR = IP
pi_list = range(PI_START_SUFFIX,PI_END_SUFFIX+1) # returns [start, ..., end-1]

print "Available PIs(" + str(len(pi_list)) + "): " + str(pi_list)

pi_ips = []
for i in pi_list:
	pi_ips.append(MNG_PREFIX+str(i))

for pi in pi_ips:

	print "Running command: " + cmd + " on " + pi + "."
	s = ssh.Connection(pi, USER , password = PASSWD)
	s.execute(cmd)
	s.close()

print "Runlevel updated!\n"
