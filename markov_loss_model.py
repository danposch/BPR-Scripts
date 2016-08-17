# @author theuerse
# loss model representing a Markov loss model
from loss_model import *

#  state p13 [ p31 [ p32 [ p23 [ p14]]]] ... state-transition probabilities
P13 = [0.5, 0.5]
P31 = [99.5, 99.5]
P23 = [0,0]
P32 = [0,0]
P14 = [0,0]
NUM_STATES = 2

def getLossCmd():
	if NUM_STATES == 1:
		PROBABILITIES = [rnd(P13)]
	elif NUM_STATES == 2:
		PROBABILITIES = [rnd(P13), rnd(P31)]
	elif NUM_STATES == 3:
		PROBABILITIES = [rnd(P13), rnd(P31),rnd(P23), rnd(P32)]
	elif NUM_STATES == 4:
		PROBABILITIES = [rnd(P13), rnd(P31),rnd(P23), rnd(P32), rnd(P14)]
	else:
		raise ValueError("The number of states must be 1,2,3 or 4")

	return " loss state " + ' '.join(str(p) for p in PROBABILITIES)
