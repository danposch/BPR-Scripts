#@author dposch

import os
import paramiko
import ssh_lib as ssh
import node_parser as np
import re as re
from apps import *
import time

def startApps(pi_list, property_list, MNG_PREFIX, PI_START_SUFFIX):

	print "Starting Simulations:"

	server_apps = []
	client_apps = []
	for pi in pi_list:
		for p in property_list:
			if pi - PI_START_SUFFIX == p.server:
				server_apps.append(pi)
				break

		if pi not in server_apps:
			for p in property_list:
				if pi - PI_START_SUFFIX == p.client:
					client_apps.append(pi)
					break

	print "Starting first \"Server\" Apps: " + str(server_apps)
	for server in server_apps:
		startAppOnPi(MNG_PREFIX+str(server))

	print "Starting now \"Client\" Apps: " + str(client_apps)
	client_ips=[]
	for client in client_apps:
		startAppOnPi(MNG_PREFIX+str(client))
		client_ips.append(MNG_PREFIX+str(client))

	print "All Apps are Up and Running!\n"
	return client_ips

def startAppOnPi(pi):

	print "Starting App on pi: " + pi

	s = ssh.Connection(pi, 'root', password = 'pi')

	files = s.execute("ls /home/nfd/")

	hasApp = False
	for f in files:
		if re.match("app.sh", f):
			hasApp = True

	if hasApp:
		s.execute("screen -d -m /home/nfd/app.sh")
		s.close()
	else:
		print "Error: There is no app.sh on this Pi! Exiting.."
		s.close()
		exit(-1)

def waitForAppsToFinish(client_ips):
	
	print "Waiting for all TrackApps to finish:"

	for pi in client_ips:
		s = ssh.Connection(pi, 'root', password = 'pi')
		
		while(True):
			res = s.execute("ps ax | grep -v grep | grep " + getTrackApp())
			
			if(len(res) == 0):
				break

			print "TrackApp still running on Pi: " + pi + " (Sleeping... 60 sec)"
			time.sleep(60)
		
		s.close()
	print "All TrackApps have finished\n"



