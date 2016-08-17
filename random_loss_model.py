# @author theuerse
# loss model representing independent loss probability
from loss_model import *

# random PERCENT
LOSS_PR = [0.000, 1] # [%],  min nonzero value =  0.0000000232%

def getLossCmd():
	return " loss random " + rnd(LOSS_PR)
