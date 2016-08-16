import os
import paramiko
import ssh_lib as ssh
import node_parser as np
import re as re
from apps import *
import time

def startLogging(pi_list, PI_START_SUFFIX, MNG_PREFIX):
	
	print "Starting Logging on all PIs:"

	for pi in pi_list:

		pi = MNG_PREFIX+str(pi)
		print "Start Logging on Pi: " + pi

		s = ssh.Connection(pi, 'root', password = 'pi')
		s.execute("nfd-status &> /home/nfd/start.nfd-status.log")
		s.put("logging", "/etc/cron.d/logging")
		s.close()

	print "All Pis started logging!\n"

def stopLogging(pi_list, PI_START_SUFFIX, MNG_PREFIX):
	
	print "Starting Logging on all PIs:"

	for pi in pi_list:

		pi = MNG_PREFIX+str(pi)
		print "Stopping Logging on Pi: " + pi

		s = ssh.Connection(pi, 'root', password = 'pi')
		s.execute("rm -f /etc/cron.d/logging")
		s.execute("nfd-status &> /home/nfd/end.nfd-status.log")
		s.close()

	print "All Pis stopped logging!\n"
