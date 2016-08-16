#Settings for Apps

#["saf", "broadcast", "best-route", "ncc", "omccrf"]
FORWARDING_STRATEGY = "broadcast"

PRODUCER_APP = "dashproducer"
PRODUCER_PARAMETER = "-s 4096 -f 300 -b /home/nfd/data/concatenated/"

CONSUMER_APP = "dashplayer"
CONSUMER_ADAPTATION_LOGIC = "player::SVCBufferAdaptationLogic"
CONSUMER_PARAMETER = "-r 2000 -t 2880 -l 200 -a " + CONSUMER_ADAPTATION_LOGIC


def getConsumerCommand(consumer, producer):
	return CONSUMER_APP + " --name " + "/"+FORWARDING_STRATEGY+"/"+str(producer) + "/concatenated-3layers-server" +str(producer)+ ".mpd " + CONSUMER_PARAMETER + " -o /home/nfd/consumer-PI_" +str(consumer)+".log"

def getProducerCommand(producer):
	return PRODUCER_APP + " -p " + "/"+FORWARDING_STRATEGY+"/"+str(producer) + " " + PRODUCER_PARAMETER

def getTrackApp():
	return CONSUMER_APP
