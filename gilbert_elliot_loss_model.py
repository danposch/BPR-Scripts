# @author theuerse
# loss model representing a Gilbert-Elliot loss model
from loss_model import *

# Gilbert-Elliot loss model
# p     ... transition probability to bad state (loss probability)
# r     ... transition probability to good state ((1-r) ... burst duration)
# (1-h) ... loss probability in the bad state
# (1-k) ... loss probability in the good state

# gemodel p [ r [ 1-h [ 1-k ]]]
P = [0.28, 0.297]
R = [0.9, 0.967]
ONE_MINUS_H = [0, 0]
ONE_MINUS_K = [0.05, 0.05986]
KIND = "GilbertElliot"

def getLossCmd():
	if KIND == "Bernoulli":
		PROBABILITIES = [rnd(P)]
	elif KIND == "SimpleGilbert":
		PROBABILITIES = [rnd(P), rnd(R)]
	elif KIND == "Gilbert":
		PROBABILITIES = [rnd(P), rnd(R), rnd(ONE_MINUS_H)]
	elif KIND == "GilbertElliot":
		PROBABILITIES = [rnd(P), rnd(R), rnd(ONE_MINUS_H), rnd(ONE_MINUS_K)]
	else:
		raise ValueError("'" + kind + "' : This kind is not supported by this loss model." +
			"[Bernoulli,SimpleGilbert,Gilbert,GilbertElliot]")

	return " loss gemodel " + ' '.join(str(p) for p in PROBABILITIES)
