#@author theuerse
# loss model representing a Gilbert-Elliot loss model
import random

# Gilbert-Elliot loss model
# p     ... loss probability
# (1-r) ... burst duration
# (1-h) ... loss probability in the bad state
# (1-k) ... loss probability in the good state

# gemodel p [ r [ 1-h [ 1-k ]]]
P_MIN = 0.28
P_MAX = 0.297
R_MIN = 0.9
R_MAX = 0.967
ONE_MINUS_H_MIN = 0
ONE_MINUS_H_MAX = 0
ONE_MINUS_K_MIN = 0.05
ONE_MINUS_K_MAX = 0.05986
ROUNDING_DIGIT = 5
KIND = "GilbertElliot"


def rnd(MIN,MAX):
	return str(round(random.uniform(MIN, MAX), ROUNDING_DIGIT))

def getLossCmd():
	if KIND == "Bernoulli":
		PROBABILITIES = [rnd(P_MIN, P_MAX)]
	elif KIND == "SimpleGilbert":
		PROBABILITIES = [rnd(P_MIN,P_MAX), rnd(R_MIN,R_MAX)]
	elif KIND == "Gilbert":
		PROBABILITIES = [rnd(P_MIN,P_MAX), rnd(R_MIN,R_MAX),
			rnd(ONE_MINUS_H_MIN, ONE_MINUS_H_MAX)]
	elif KIND == "GilbertElliot":
		PROBABILITIES = [rnd(P_MIN,P_MAX), rnd(R_MIN,R_MAX),
			rnd(ONE_MINUS_H_MIN, ONE_MINUS_H_MAX), rnd(ONE_MINUS_K_MIN, ONE_MINUS_K_MAX)]
	else:
		raise ValueError("'" + kind + "' : This kind is not supported by this loss model." +
			"[Bernoulli,SimpleGilbert,Gilbert,GilbertElliot]")

	return " loss gemodel " + ' '.join(str(p) for p in PROBABILITIES)
