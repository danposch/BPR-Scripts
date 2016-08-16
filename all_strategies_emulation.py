import os
import time
import subprocess
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

RUNS = 35
#STRATEGIES=["broadcast", "best-route", "ncc", "saf", "omccrf"]
STRATEGIES=["omccrf"]


BW = {}
BW["LowBW"] = [2000,3000]
BW["MediumBW"] = [3000,4000]
BW["HighBW"] = [4000,5000]

CONNECTIVITY = {}
CONNECTIVITY["LowCon"] = 0.10
CONNECTIVITY["MediumCon"] = 0.15
CONNECTIVITY["HighCon"] = 0.20

def deleteFile(path):
	if os.path.isfile(path):
		os.remove(path)
	return

def setForwardingStrategy(strategy):
	#move old file
	os.rename("apps.py", "apps_old.py")

	old_f = open("apps_old.py", "r")
	new_f = open("apps.py", "w")

	for line in old_f:
		if "FORWARDING_STRATEGY =" in line:
			new_f.write("FORWARDING_STRATEGY = \"" + s +"\"\n")
		else:
			new_f.write(line)

	old_f.close()
	new_f.close()

def setBandwith(bw):
	#move old file
	os.rename("rand_network.py", "rand_network_old.py")

	old_f = open("rand_network_old.py", "r")
	new_f = open("rand_network.py", "w")

	for line in old_f:
		if "MIN_BANDWIDTH =" in line:
			new_f.write("MIN_BANDWIDTH = " + str(bw[0]) +"\n")
		elif "MAX_BANDWIDTH =" in line:
			new_f.write("MAX_BANDWIDTH = " + str(bw[1]) +"\n")
		else:
			new_f.write(line)

	old_f.close()
	new_f.close()

def setConnectivity(con):
	#move old file
	os.rename("rand_network.py", "rand_network_old.py")

	old_f = open("rand_network_old.py", "r")
	new_f = open("rand_network.py", "w")

	for line in old_f:
		if "EDGE_PROBABILITY =" in line:
			new_f.write("EDGE_PROBABILITY = " + str(con) +"\n")
		else:
			new_f.write(line)

	old_f.close()
	new_f.close()

#main
different_settings = len(STRATEGIES)*len(BW)*len(CONNECTIVITY)
print "Performing " + str(different_settings) + " Settings a " + str(RUNS) + " runs (" + str(different_settings*RUNS) + " total runs)."
print "Strategies: " + str(STRATEGIES)
print "Bandwidths: " + str(BW)
print "Connectivities: " + str(CONNECTIVITY)

time.sleep (5)
setting_counter = 1
for s in STRATEGIES:

        #first remove old genereated .pyc files, or python does not "re-compile" them correctly 
        deleteFile("apps.pyc")
        deleteFile("rand_network.pyc")

	print "Starting eumulations for Strategy: " + s
	setForwardingStrategy(s)	

	for bw in BW:
		
		print "Setting BW Level: " + str(bw) + " (" + str(BW[bw]) +")" 		
		setBandwith(BW[bw])

		for con in CONNECTIVITY: 

			print "Setting Connectivity Level: " + str(con) + " (" + str(CONNECTIVITY[con])+")"
			setConnectivity(CONNECTIVITY[con])

			print "Starting Runs for Setting: " + str(setting_counter) + "/" + str(different_settings)

			sysCall = ["python"] + ["emulation.py"] + ["--fw-strategies="+str(s)] + ["--emulation-runs=" + str(RUNS)] +	["--result-folder=" + os.getenv("HOME") + "/emulation_results/" + s + bw +con]
			print "sysCall=" + str(sysCall)

			proc=subprocess.Popen(sysCall, cwd=os.getcwd())
			proc.communicate() # wait until finished
			setting_counter += 1

print "Emulation Jobs finished!!"
