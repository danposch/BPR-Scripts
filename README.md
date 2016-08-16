# BPR-Scripts
Scripts for the NDN Banana Pi Testbed

![dependencies](https://cloud.githubusercontent.com/assets/16044516/17700969/37d347da-63c8-11e6-9adb-403c773a09a9.png)

Tasked with managing, monitoring and running emulations on a larger number of homogenous nodes (BananaPi-routers to be specific), a sensible level of automation via scripting is essential.

A certain familiarity with the Python programming language and the GNU/Linux operating system helps a great deal with understanding the operation of the scripts and the NDN-Testbed as a whole.

The scripts are in productive use and generally do their job well, although they are not free of typos, may contain spelling errors and may generally not be implemented perfectly in regards to algorithmic beauty or commentary.

The primary concerns were the functionality and correctness of the scripts, you are free to improve them / modify them to suit your needs :-) .

For additional information regarding the scripts or the NDN-Testbed itself, please visit [http://icn.itec.aau.at/].

## emulation
------------
![emulation](https://cloud.githubusercontent.com/assets/16044516/17700974/3d1eb2e2-63c8-11e6-9cd8-442ece681399.png)
### all_strategies_emulation.py
Performs a given number of emulation-runs for every given forwarding-strategy, bandwidth-range and connectivity.
This script is intended to be used with the NDN-Applications from [https://github.com/danposch/ndn-apps].
This script changes the files apps.py and rand_network.py before deploying the network in oder to achieve the different configurations, creating the apps_old.py and rand_network_old.py in the process.

### emulation.py
Takes parameters, creates (if necessary) a random network-topology, calls deploy_network.py to establish the virtual network overlay, starts/stops the logging, starts/stops the emulation-applications on the nodes, stops NFDs and logging after emulation completion, collects and stores logs.

In everyday use, a virtual console was opened on the gateway-server (man screen), calling emulation.py (or all_strategies...), redirecting its standard-output to a file and detaching from this virtual console. This made the execution of the emulation independent of any connected client, with the options to resume the console session from any connected host and monitor the progress via the log-file.

For more information on the emulation-cycle, please visit [http://icn.itec.aau.at/ndn-network/qickstart-your-first-emulation/].

### nfd_kill.py
Utility-script for emulation.py, used to stop the NFDs on ALL nodes.
Basically connecting to all nodes via SSH and issuing the "nfd-stop" command.

### node_parser.py
Acts as utility-script for emulation.py, parses network-topology files for usage by deploy_network.py.
The network-topology-file which contains the network-properties as comma seperated values is read and respective lists of classes are provided for the deploy_network.py script.

### pi_logging.py
Utility for emulation.py, used to start/stopp logging NFD-status and node-status  on ALL nodes.
The node-status-files are created using the "logging" CRON-job.

### rand_network.py
Utility for emulation.py, creates random network topology-files (generatd_network_top.txt) depending on the given emu-run number and some parameters contained inside the file.

The random topology generator also supports the addition of loss on the virtual links.
Using netem (man netem, man tc-netem) under the hood, random- Markov- and Gilbert-Elliot loss-models may be used.
Given a value for the property LOSS_MODEL, the corresponding python-script is called in order to create a valid netem-command to emulate a certain kind of loss.
The respective commands become part of the link-descriptions in generated_network_top.txt, using no loss model creates topology-files without any mention of loss.
The values for LOSS_MODEL may be "", "random_loss_model", "markov_loss_model" and "gilbert_elliot_loss_model".

### start_apps.py
Utility for emulation.py, used to start the emulation-applications on ALL nodes, provides the means to wait for certain apps on ALL nodes to finish.

When starting the applications, all server-applications are started before starting the client-applications.

The return value of apps.py's method getTrackApp() returns the name of the applications to wait for (e.g. the CONSUMER_APPs / "consumer").

### deploy_network.py
Utility for emulation.py, creates and runs configuration files/scripts (network.sh, app.sh, client.sh) to establish the virtual overlay network. Also configures the routing information in the individual NFDs and starts them.

### garther_results.py
Utility for emulation.py, get different log-files of ALL nodes and save them in a own directory.

The collected files include  consumer-application-results, pi-status-files, NFD status-logs and NFD-cache-logs.
Feel free to adapt this script to garther (just) the files/results you are interested in/your applications produce.

### random_loss_model.py
Returns a command-string for tc's netem in order to emulate a independent (packet-)loss probability.

The command is written to generated_network_top.txt, parsed by node_parser.py and used by deploy_network.py to create the network.sh - bash-files which setup the individual node's network-connections.

### markov_loss_model.py
Returns a command-string for tc's netem in order to emulate a (possibly bursty) packet-loss using a Markov-chain.

### gilbert_elliot_loss_model.py
Returns a command-string for tc's netem in order to emulate a (possibly bursty) packet-loss using a variation of the Gilbert-Elliot-loss-model. (Bernoulli, Simple Gilbert, Gilbert, GilbertElliot)

### apps.py
Utility-script for deploy_network.py, containing settings for the creation of bash-scripts defining/starting the emulation-applications on the individual nodes.

Before running a emulation, the content of apps.py can be modified in order to define the consumer-/producer-applications to be executed and their respective parameters. E.g. all_strategies_emulation.py modifies apps.py.

### allPaths.py
Utility-script for emulation.py, returning all possible paths connecting two nodes in a directed graph.
Used by deploy_network.py to configure the route-entries in the NFD-Forwarding-Information-Bases (FIB) of the individual nodes (if "all routes" is selected).


## management
--------------
![management](https://cloud.githubusercontent.com/assets/16044516/17700982/415dd234-63c8-11e6-923a-a2f94f5520c1.png)
### deploy_code.py
Checks out and installs the latest versions of emulation-software on ALL nodes (Pis).
This involves cloning/pulling, building and installing specific GitHub-repositories containing emulation-applications and their dependencies.
Currently, "ITEC-NFD, NDN-apps, libdash, ndn-DemoApps" are set up, feel free to adapt this script to your needs.

The operating system and installed packages of the nodes are not updated.


### deploy_file.py
Copies a given file to ALL nodes to a given destination, as a given user. The given user must possess permission to write to the destination.
Used to e.g. deploy modified configuration-files (NFD) on the nodes.

### install_packages.py
Installs a given package (apt-get install xxx) as a given user on ALL nodes. (user must have sufficient privileges on the nodes)
Used to e.g. to install additionally needed packages after already having deployed the Pi-Image on the individual nodes.

### reboot.py
Reboots ALL nodes.
In our experience, the nodes/Pis run very reliably, but certain situations (application error, testing a config-change persists, ...) necessitate a collective reboot.

### rsync.sh
An example of a command to synchronize a local pi-script-folder with that one on the pi-gateway using the program rysnc.
(man rsync)

### runcommand.py
Executes a given command as a given user on ALL nodes.
Connects to the individual Pis using SSH an executes the command.

### temperaturs.py
Prints the SOC- and HDD-temperatures of ALL nodes. A secondary use can be to check the availability/reachability of the nodes, as this script fails if one node is not reachable / crashed (SSH connection cannot be established).

## logging
------------
![logging](https://cloud.githubusercontent.com/assets/16044516/17700987/45ce8ae8-63c8-11e6-8c75-9530c69648f4.png)
### client.sh
A bash-script which garthers the current system state of a node (running services, CPU-load, memory, temperatures, ...), formats it in JSON and prints the information to stdout.

Executing this script and redirecting its output to a file is the basis of a number of logging functionalities.  

Based on a script by Remy van Elst (#Copyright (c) 2012 Remy van Elst).

It is advisable to try and run this script manually for the first time in order to check that all system-status-information can be collected correctly / all necessary sensors are available.

### raymon-client
File containing the CRON-command to periodically create a status-logfile using client.sh.

Parameterized to perform the creation of the file every half hour, and saving the JSON-file in the document-root of the node, this command acts as the information-source of the normal logging process (netstat).

The nodes create status-files periodically and make them available over their light-weight webservers.

The gateway-server pulls the files from the webservers (if necessary) and displays an overview.

### logging
File containing the CRON-command to periodically create a status-logfile using client.sh.

This command is installed/removed as a CRON-job by emulation.py before/after a emulation-run (using pi_logging.py).

### emulation_logging.sh
A bash-script periodically calling client.sh and saving its output as a time-coded JSON-file.

Once started, it runs as long as EMUTIME seconds plus some safety margin.

### realtime_logging
Bash-script handling the execution of the realtime_logging.sh as a daemon.
(/etc/init.d/skeleton has served as a template.)

The realtime_logging-daemon is usually running by default, you may want to disable it for performance-reasons, especially if you don't use the realtime-logging visualization netvis.

### realtime_logging.sh
A bash-script executing the actions for realtime_logging.
First, client.sh is called to obtain a JSON-file representing the current system-status. Next, the status-file and a DASH-client-logfile (created by dash-client-application) are put on a samba-share directory on the pi-gateway.

In contrast to the "normal" logging process (netstat), where the gateway pulls the information from the nodes, here the nodes actively push their information onto the gateway. Also the time until new data is created / arriving is much shorter (5 seconds compared to 30 minutes).

### emu.log
An example for the logging-output created by executing emulation.py. Generally describes the state of the overall process (what happens, how far along is the emulation in terms of runs, exceptions as reason of the termination of the emulation-process)

### clientlogshistory
File containing a CRON-command to actively issue a PHP-script on the gateway-server to retrieve and archive the latest status-log-files of the individual nodes.

A slightly modified version (different time-interval) of this command runs on the gateway-server, periodically (e.g. hourly) getting/archiving the current node-status-files.

## network-topology (examples)
------------------------------
![networktopologies](https://cloud.githubusercontent.com/assets/16044516/17700993/4a05cd4c-63c8-11e6-961c-e636fbc3e264.png)
### network.txt
An illustrative example of a network-topology-file.
Especially useful if one is just in the process of getting familiar with the network-topology-file-format.

### generated_network_top.txt
A network-topology-file, generated by rand_network.py, usable by deploy_network.py after being parsed by node_parser.py.

The file contains three sections, separated by lines beginning with a '#'.

The first section informs about the total number of nodes in the network-topology.

(e.g.) 20

The second section specifies all edges in the network-topology:


0,1,4832,4453,1,4

=> There is a directed edge from node 0 to node 1, the bandwidth of this link is 4832[kbits], the delay is 1[ms]

=> There is a directed edge from node 1 to node 0, the bandwidth of this link is 4453[kbits], the delay is 4[ms]

The third section specifies the roles of the individual nodes and their affiliations.

4,3

9,19

2,11

6,3

=> node 4 is a client and belongs to / wants data from server 3

=> node 9 is a client and belongs to / wants data from server 19

...

## utility
------------
![utility](https://cloud.githubusercontent.com/assets/16044516/17700997/4d7734f2-63c8-11e6-98f7-f6cbd3da8d85.png)
### ssh_lib.py
A friendly python SSH2 interface, used by virtually all management and some emulation-scripts.

A slightly modified version of a script available under http://snipplr.com/view/48033/, a big thank you goes to the author whoever/wherever he/she may be.
