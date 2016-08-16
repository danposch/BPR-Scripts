#!/bin/bash

x=`ip -f inet a | grep "eth0.101" | awk '/inet/{printf $2 }'`
x=${x%/*}
oc1=${x%%.*}
x=${x#*.*}
oc2={x%%.*}
x=${x#*.*}
oc3=${x%%.*}
x=${x#*.*}
piID=$((${x%%.*} - 10 ))


#cd /run/shm

while true; do
	
	cd /run/shm
        /bin/bash /root/client.sh > "/run/shm/PI$piID.json" 2>&1
        smbclient -U www-data //192.168.0.1/pilogging -c "put PI$piID.json" www
	cd /home/nfd/
        smbclient -U www-data //192.168.0.1/pilogging -c "put consumer-PI_$piID.log" www
        sleep 5    # the desired logging interval
done
