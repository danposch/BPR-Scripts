#@author dposch

import os
import paramiko
import ssh_lib as ssh
import node_parser as np
import re

def gatherResults(pi_list, MNG_PREFIX, DESTINATION_FOLDER, emu_run, client_ips, PI_START_SUFFIX):

	DESTINATION_FOLDER = DESTINATION_FOLDER+"/run_"+str(emu_run)

	print "Gathering Results in: " + DESTINATION_FOLDER

	os.makedirs(DESTINATION_FOLDER)

	gatherConsumerResults(client_ips, DESTINATION_FOLDER)
	gatherPiStats(pi_list, MNG_PREFIX, DESTINATION_FOLDER, PI_START_SUFFIX)
	gatherNFDStatusLogs(pi_list, MNG_PREFIX, DESTINATION_FOLDER, PI_START_SUFFIX)
	gatherNFDCacheLogs(pi_list, MNG_PREFIX, DESTINATION_FOLDER, PI_START_SUFFIX)
	
	print "Got all Resutls!\n"

def gatherConsumerResults(client_ips, DESTINATION_FOLDER):

	for pi in client_ips:
		print "Trying to get Result from TrackApp of Pi: " + pi

		s = ssh.Connection(pi, 'root', password = 'pi')
		files = s.execute("ls /home/nfd/")

		for f in files:
			if re.match("consumer-PI_[0-9]+\.log", f):

				f = f.rstrip()
				src = "/home/nfd/" + f
				dest = DESTINATION_FOLDER + "/"+ f

				print "Gathered \"" + f + "\" from src: " + src + " to " + dest
				s.get(src, dest)
				break

		s.close()

def gatherPiStats(pi_list, MNG_PREFIX, DESTINATION_FOLDER, PI_START_SUFFIX):

	for pi in pi_list:
		print "Gathering Pi-Stats from " + MNG_PREFIX+str(pi)

		s = ssh.Connection(MNG_PREFIX+str(pi), 'root', password = 'pi')
		files = s.execute("ls /tmp/logs/stat-*.json")
		
		for f in files:
			f = f.rstrip().split('/')[-1]
			src = "/tmp/logs/" + f
			f = f.replace("stat-", "stat-PI_"+str(pi-PI_START_SUFFIX) +"_" )
			dest= DESTINATION_FOLDER + "/"+ f
			s.get(src, dest)

		s.close()

def gatherNFDStatusLogs(pi_list, MNG_PREFIX, DESTINATION_FOLDER, PI_START_SUFFIX):

	for pi in pi_list:
		print "Gathering NFD-Status Logs from " + MNG_PREFIX+str(pi)

		s = ssh.Connection(MNG_PREFIX+str(pi), 'root', password = 'pi')
		files = s.execute("ls /home/nfd/*nfd-status.log")

		for f in files:
			f = f.rstrip().split('/')[-1]
			src = "/home/nfd/" + f
			f = f.replace("nfd-status", "nfd-status-PI_"+str(pi-PI_START_SUFFIX))
			dest= DESTINATION_FOLDER + "/"+ f
			s.get(src, dest)

		s.close()

def gatherNFDCacheLogs(pi_list, MNG_PREFIX, DESTINATION_FOLDER, PI_START_SUFFIX):

	for pi in pi_list:
		print "Gathering NFD-Cachelog from " + MNG_PREFIX+str(pi)

		s = ssh.Connection(MNG_PREFIX+str(pi), 'root', password = 'pi')
		files = s.execute("ls /tmp/nfd_cachehits.txt")
		
		for f in files:
			f = f.rstrip().split('/')[-1]
			src = "/tmp/" + f
			f = f.replace("nfd_cachehits", "nfd_cachehits-PI_"+str(pi-PI_START_SUFFIX))
			dest= DESTINATION_FOLDER + "/"+ f
			s.get(src, dest)

		s.close()
