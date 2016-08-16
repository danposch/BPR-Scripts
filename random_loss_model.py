#@author theuerse
# loss model representing independent loss probability
# imported by rand_network.py, 	random.seed(EMU_RUN_NUMBER) already done
import random

# random PERCENT
MIN_LOSS_PR = 0.000 # [%],  min nonzero value =  0.0000000232%
MAX_LOSS_PR = 1		# [%]
ROUNDING_DIGIT = 5

def getLossCmd():
	return " loss random " + str(round(random.uniform(MIN_LOSS_PR, MAX_LOSS_PR), ROUNDING_DIGIT))
