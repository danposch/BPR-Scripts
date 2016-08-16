#@author dposch

import os
import paramiko
import ssh_lib as ssh
import node_parser as np
import time

def killNFDs(pi_list, MNG_PREFIX, PI_START_SUFFIX):

	print "Stopping all NFDs:"

	for pi in pi_list:

		pi = MNG_PREFIX+str(pi)
		print "Stopping NFD: " + pi

		s = ssh.Connection(pi, 'root', password = 'pi')
		s.execute("nfd-stop")
		s.close()

	print "NFDs Stopped!\n"
	time.sleep(10)#sleep 10 sec to ensure nfd-stop(s) finished before gathering the results
