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

print "Deploying File:"

SRC_FILE = ""
DEST_FILE = ""
USER = ""
PASSWD = ""

if len(sys.argv) != 5:
	print "Invalid Parameters -- Usage:"
	print "src_file, dest_file, user, passwd"
	exit(-1)

SRC_FILE = str(sys.argv[1])
DEST_FILE = str(sys.argv[2])
USER = str(sys.argv[3])
PASSWD = str(sys.argv[4])

# available pis: PREFIX.NR = IP
pi_list = range(PI_START_SUFFIX,PI_END_SUFFIX+1) # returns [start, ..., end-1]

print "Available PIs(" + str(len(pi_list)) + "): " + str(pi_list)

pi_ips = []
for i in pi_list:
	pi_ips.append(MNG_PREFIX+str(i))

for pi in pi_ips:

	print "Copying " + SRC_FILE + " to " + pi + " " + DEST_FILE
	s = ssh.Connection(pi, USER , password = PASSWD)
	s.put(SRC_FILE, DEST_FILE )
	s.close()

print "File Deployed!\n"
