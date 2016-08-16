#Settings for Apps

#["saf", "broadcast", "best-route", "ncc", "omccrf"]
FORWARDING_STRATEGY = "omccrf"

PRODUCER_APP = "producer"
PRODUCER_PARAMETER = "-s 4096 -f 300"

CONSUMER_APP = "consumer"
CONSUMER_PARAMETER = "-r 60 -t 1800 -x -l 1000" 


def getConsumerCommand(consumer, producer):
	return CONSUMER_APP + " -p " + "/"+FORWARDING_STRATEGY+"/"+str(producer) + " " + CONSUMER_PARAMETER + " -o /home/nfd/consumer-PI_" +str(consumer)+".log"

def getProducerCommand(producer):
	return PRODUCER_APP + " -p " + "/"+FORWARDING_STRATEGY+"/"+str(producer) + " " + PRODUCER_PARAMETER

def getTrackApp():
	return CONSUMER_APP
