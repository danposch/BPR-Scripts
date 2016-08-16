#!/bin/bash

# SECONDS is an internal varilable providing the run time of the script in seconds
end=$((SECONDS+$$$EMUTIME$$$+120))

while [ $SECONDS -lt $end ]; do
	sh /root/client.sh > "/tmp/logs/stat-`date +\%Y-\%m-\%H\_\%k:\%M:\%S`.json" 2>&1 
	sleep $$$LOGGINGINTERVAL$$$    # the desired logging interval
done
