#!/usr/bin/env python

###########
# imports
###########
from enum import Enum

###########
# internal classes
###########
class State(Enum):
	RUN_FORWARD = 1
	RUN_FORWARD_BREAK = 2
	RUN_BACKWARD = 3
	STOP = 4
	ERROR = 5

