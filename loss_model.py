# @author theuerse
# base settings/methods for all loss models
import random

ROUNDING_DIGIT = 5

def rnd(BOUNDS):
	return str(round(random.uniform(BOUNDS[0], BOUNDS[1]), ROUNDING_DIGIT))
