#!/bin/bash
#Copyright (c) 2012 Remy van Elst
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

# Network interface for the IP address
iface="eth0.101"
# network interface for traffic monitoring (RX/TX bytes)
iface2="eth0.102"

#json start
echo -n "{"

echo -n "\"Services\": { "
SERVICE=lighttpd
if ps ax | grep -v grep | grep $SERVICE > /dev/null; then echo -n "\"$SERVICE\" : \"running\","; else echo -n "\"$SERVICE\" : \"not running\","; fi
SERVICE=nfd
if ps ax | grep -v grep | grep $SERVICE > /dev/null; then echo -n "\"$SERVICE\" : \"running\","; else echo -n "\"$SERVICE\" : \"not running\","; fi
SERVICE=producer
if ps ax | grep -v grep | grep $SERVICE > /dev/null; then echo -n "\"$SERVICE\" : \"running\","; else echo -n "\"$SERVICE\" : \"not running\","; fi
SERVICE=$$$TRACKAPP$$$
if ps ax | grep -v grep | grep $SERVICE > /dev/null; then echo -n "\"$SERVICE\" : \"running\""; else echo -n "\"$SERVICE\" : \"not running\""; fi
#LAST SERVICE HAS TO BE WITHOUT , FOR VALID JSON!!!
echo -n " }, "

#disk
echo -n "\"Disk\" : { ";
echo -n "\""
#df -h -T -xtmpfs -xdevtmpfs -xrootfs | awk '{print "\"device\" : \""$1"\", \"type\" : \""$2"\", \"total\" : \"" $3"\", \"used\" : \""$4"\", \"free\" : \""$5"\", \"percentage\" : \""$6"\", \"mounted on\" : \""$7"\""'}
disk_usage=`df -h --total | awk  ' /total/ { print "total\" : \""$2"\", \"used\" : \""$3"\", \"free\" : \""$4"\", \"percentage\" : \""$5" " }'`
echo -n "$disk_usage\" }, "

# Load
echo -n "\"Load\" : \""
#if $(echo `uptime`  | sed 's/  / /g' | grep -E "min|days" >/dev/null); then echo `uptime` | sed s/,//g | awk '{ printf $10 }'; else echo `uptime` | sed s/,//g| awk '{ printf $8 }'; fi
my_uptime_1=`uptime | grep -ohe 'load average[s:][: ].*' | awk '{ print $4 }' | sed s/,//g`
echo -n "$my_uptime_1\", "

#Users:
echo -n "\"Users logged on\" : \""
#if $(echo `uptime` | sed 's/  / /g' | grep -E "min|days" >/dev/null); then echo `uptime` | sed s/,//g | awk '{ printf $6 }'; else echo `uptime` | sed s/,//g| awk '{ printf  $4 }'; fi
my_uptime_2=`uptime | grep -ohe '[0-9.*] user[s,]' | awk '{ print $1 }'`
echo -n "$my_uptime_2\", "

#Uptime 
echo -n "\"Uptime\" : \""
#if $(echo `uptime` | sed 's/  / /g' | sed 's/,//g' | grep -E "days" >/dev/null); then echo `uptime` | sed s/,//g | awk '{ printf $3" "$4 }'; else echo `uptime` | sed s/,//g| awk '{ printf  3 }'; fi
my_uptime_3=`uptime | grep -ohe 'up .*' | sed 's/,//g' | awk '{ print $2" "$3 }'`
echo -n "$my_uptime_3\", "


# Memory
echo -n "\"Free RAM\" : \""
free -m | grep -v shared | awk '/buffers/ {printf $4 }'
echo -n "\", "
echo -n "\"Total RAM\" : \""
free -m | grep -v shared | awk '/Mem/ {printf $2 }'
echo -n "\", "



# local ip
echo -n "\"IPv4\" : \""
ip -f inet a | grep "$iface" | awk '/inet/{printf $2 }' 
echo -n "\","

#hostname
echo -n "\"Hostname\" : "
echo -n "\"`hostname`\", "

# network traffic
rxbytes=`/sbin/ifconfig $iface2 | awk '{ gsub(/\:/," ") } ; { print  } ' | awk '/RX\ b/ { print $3 }'`
echo -n "\"rxbytes\" : \""
echo -n $rxbytes
echo -n "\", "

txbytes=`/sbin/ifconfig $iface2 | awk '{ gsub(/\:/," ") } ; { print  } ' | awk '/RX\ b/ { print $8 }'`
echo -n "\"txbytes\" : \""
echo -n $txbytes
echo -n "\", "

# traffic per virtual link
my_ip_man=`ip -f inet a | grep "$iface" | awk '/inet/{printf $2 }'`
my_ip_man=${my_ip_man::-3}
my_ip_emu=`ip -f inet a | grep "$iface2" | awk '/inet/{printf $2 }'`
my_ip_emu=${my_ip_emu::-3}
ip_out=`iptables -L -v -n -x`
mode="NONE"
declare -A traffic
while IFS= read -r line; do

        if [[ $line == Chain\ INPUT* ]]; then
                mode="INPUT"

        elif [[ $line == Chain\ FORWARD* ]]; then
                mode="FORWARD"

        elif [[ $line == Chain\ OUTPUT* ]]; then
                 mode="OUTPUT"

        elif [[ $mode == "INPUT" ]]; then

                if [[ $line != *pkts* ]] && [[ $line == *ACCEPT* ]]; then
                        IFS=' ' read  pkts bytes target prot opt in out source dest <<< $line

                        if [[ $source == 192.168.1.* ]] && [[ $dest == $my_ip_emu ]]; then
                                traffic[$source]=$bytes
                                #[key] = value
                                #echo $traffic[$source] =  ${traffic[$source]}
                        fi
                fi

        elif [[ $mode == "OUTPUT" ]]; then
                if [[ $line != *pkts* ]] && [[ $line == *ACCEPT* ]]; then
                        IFS=' ' read  pkts bytes target prot opt in out source dest <<< $line

                        if [[ $dest == 192.168.1.* ]] && [[ $source == $my_ip_emu ]]; then
                                traffic[$dest]=$(($bytes + ${traffic[$dest]}))
                                #echo $traffic[$dest] =  ${traffic[$dest]}
                        fi

                fi
        fi
done < <(printf '%s\n' "$ip_out")
echo -n "\"Traffic\" : { ";
t_counter=1
for entry in "${!traffic[@]}"; do
        echo -n "\"$entry\" : \""
				echo -n "${traffic[$entry]}"
				if [[ $t_counter < ${#traffic[@]} ]]; then
				        echo -n "\", "
								let t_counter=t_counter+1
				else
								echo -n "\" "
				fi
done
echo -n " }, "

# SoC temp
cputemp=`soctemp | cut -b 1-8 --complement`
echo -n "\"cputemp\" : \""
echo -n `soctemp | cut -b 1-8 --complement`
echo -n "\", "

# PMU temp
pmutemp=`pmutemp | cut -b 1-8 --complement`
echo -n "\"pmutemp\" : \""
echo -n `pmutemp | cut -b 1-8 --complement`
echo -n "\", "

ssdtemp=`hddtemp /dev/sda  | awk  '{print $4}' | cut -b 1-2`
echo -n "\"hddtemp\" : \""
echo -n $ssdtemp
echo -n "\", "

# Voltage
voltage=`cat /sys/devices/platform/sunxi-i2c.0/i2c-0/0-0034/axp20-supplyer.28/power_supply/ac/voltage_now`
echo -n "\"voltage\" : \""
echo -n $voltage
echo -n "\", "

# Current
current=`cat /sys/devices/platform/sunxi-i2c.0/i2c-0/0-0034/axp20-supplyer.28/power_supply/ac/current_now`
echo -n "\"current\" : \""
echo -n $current
echo -n "\", "

# cpu0 freq
cpu0freq=`cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq`
echo -n "\"cpu0freq\" : \""
echo -n $cpu0freq
echo -n "\", " 

# cpu1 freq
cpu1freq=`cat /sys/devices/system/cpu/cpu1/cpufreq/cpuinfo_cur_freq`
echo -n "\"cpu1freq\" : \""
echo -n $cpu1freq
echo -n "\", "

# current date
mydate=`date`
echo -n "\"date\" : \""
echo -n $mydate
echo -n "\", "

#json close
echo -n "\"JSON\" : \"close\""
echo -n " } "
