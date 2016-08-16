#@author theuerse
# loss model representing a Markov loss model
import random

#  state p13 [ p31 [ p32 [ p23 [ p14]]]]
P13_MIN = 0.5
P13_MAX = 0.5
P31_MIN = 99.5
P31_MAX = 99.5
P23_MIN = 0
P23_MAX = 0
P32_MIN = 0
P32_MAX = 0
P14_MIN = 0
P14_MAX = 0
ROUNDING_DIGIT = 5
NUM_STATES = 2

def rnd(MIN,MAX):
	return str(round(random.uniform(MIN, MAX), ROUNDING_DIGIT))

def getLossCmd():
	if NUM_STATES == 1:
		PROBABILITIES = [rnd(P13_MIN, P13_MAX)]
	elif NUM_STATES == 2:
		PROBABILITIES = [rnd(P13_MIN, P13_MAX), rnd(P31_MIN, P31_MAX)]
	elif NUM_STATES == 3:
		PROBABILITIES = [rnd(P13_MIN, P13_MAX), rnd(P31_MIN, P31_MAX),
			rnd(P23_MIN, P23_MAX), rnd(P32_MIN, P32_MAX)]
	elif NUM_STATES == 4:
		PROBABILITIES = [rnd(P13_MIN, P13_MAX), rnd(P31_MIN, P31_MAX),
			rnd(P23_MIN, P23_MAX), rnd(P32_MIN, P32_MAX), rnd(P14_MIN, P14_MAX)]
	else:
		raise ValueError("The number of states must be 1,2,3 or 4")

	return " loss state " + ' '.join(str(p) for p in PROBABILITIES)
