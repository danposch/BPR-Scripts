#@author dposch

import os
import paramiko
import ssh_lib as ssh
import node_parser as np
import apps as ap
from igraph import *
from allPaths import *
import argparse
from deploy_network import *
from nfd_kill import *
from pi_logging import *
from datetime import datetime
from gather_results import *
import rand_network as rand_network
import shutil
import sys

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)
#stop buffering of output for this script
sys.stdout = Unbuffered(sys.stdout)


#default parameters

MNG_PREFIX = "192.168.0."
EMU_PREFIX = "192.168.1."
GATEWAY = "192.168.0.1"

#argument parsing
arg_parser = argparse.ArgumentParser(description="Script for Running Emulations on the PI-Network")
arg_parser.add_argument("--network", action="store", dest="network", default="random", help="Network Topology to deploy, If set to random a random topology is generated based on parameters in rand_network.py for each emulation run")
arg_parser.add_argument("--paths", action="store", dest="paths", default="all", choices=["all", "shortest"], help="Paths for FIB entries. CAREFUL \"all\" may take very long in well connected and large scenarios!")
arg_parser.add_argument("--pi-start-suffix", action="store", dest="piStartSuffix", default=10, type=int, help="Suffix of the IP for the first PI")
arg_parser.add_argument("--pi-end-suffix", action="store", dest="piEndSuffix", default=29, type=int, help="Suffix of the IP for the last PI")
arg_parser.add_argument("--fw-strategies", action="store", dest="forwardingStrategies", default=["saf", "broadcast", "best-route", "ncc", "omccrf"], nargs="+", choices=["saf", "broadcast", "best-route", "ncc", "omccrf"], help="Forwarding Strategies for which ndn-routes are deployed")
arg_parser.add_argument("--emulation-runs", action="store", dest="runs", default=1, type=int, help="Number of Emulations to perform")
arg_parser.add_argument("--result-folder", action="store", dest="resultFolder", default=os.getenv("HOME") + "/emulation_results/")
arguments = arg_parser.parse_args()

NETWORK = arguments.network
PATHS = arguments.paths
PI_START_SUFFIX = arguments.piStartSuffix
PI_END_SUFFIX = arguments.piEndSuffix
FW_STRATEGIES = arguments.forwardingStrategies
EMULATION_RUNS = arguments.runs
if arguments.resultFolder == (os.getenv("HOME") + "/emulation_results/"):
	DESTINATION_FOLDER = arguments.resultFolder + datetime.now().strftime('%d_%m_%Y_%H:%M')
else:
	DESTINATION_FOLDER = arguments.resultFolder

print "Starting " + str(EMULATION_RUNS) + " Emulation(s): "

for emu_run in range(0,EMULATION_RUNS):

	try:
		#check if run already has been performed:
		if os.path.exists(DESTINATION_FOLDER + "/run_" + str(emu_run)):
			print "Run: " + DESTINATION_FOLDER + "/run_" + str(emu_run) + " exists.. SKIPPING!"
			continue

		print "=========================="
		print "Performing Emulation Run " + str(emu_run+1) + "/" + str(EMULATION_RUNS) + ":"

		if NETWORK == "random":
			network_top_file = rand_network.genRandomNetwork(emu_run)
		else:
			network_top_file = NETWORK

		#deploy the network and the apps and cleansup the logs
		graph, pi_list, property_list = deployNetwork(network_top_file, PATHS, PI_START_SUFFIX, PI_END_SUFFIX,
																			FW_STRATEGIES, MNG_PREFIX, EMU_PREFIX, GATEWAY)

		#start logging
		startLogging(pi_list, PI_START_SUFFIX, MNG_PREFIX)

		#start the apps	
		client_ips = startApps(pi_list, property_list, MNG_PREFIX, PI_START_SUFFIX)

		#loop until all clients finished
		waitForAppsToFinish(client_ips)

		#stop logging
		stopLogging(pi_list, PI_START_SUFFIX, MNG_PREFIX)

		#kill all NFDs
		killNFDs(pi_list, MNG_PREFIX, PI_START_SUFFIX)
	
		#collect and store logs
		gatherResults(pi_list, MNG_PREFIX, DESTINATION_FOLDER, emu_run, client_ips, PI_START_SUFFIX)

		print "Finished Emulation Run " + str(emu_run+1) + "/" + str(EMULATION_RUNS) + ":"
		print "=========================="
	except (BaseException):
		print "Encountered Exception... Deleting Files in: " + DESTINATION_FOLDER + "/run_" + str(emu_run)
		shutil.rmtree(DESTINATION_FOLDER + "/run_" + str(emu_run))
		pass #pass on to next run
