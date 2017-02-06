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

###########
# functions
###########
def set_new_state(status, new_state):
	
	# RUN_FORWARD -> RUN_BACKWARD shall not be possible, stop first
	if status["STATE"] == State.RUN_FORWARD:
		if new_state == State.RUN_BACKWARD:
			return False
	# RUN_FORWARD_BREAK -> RUN_BACKWARD shall not be possible, stop first
	elif status["STATE"] == State.RUN_FORWARD_BREAK:
		if new_state == State.RUN_BACKWARD:
			return False
	# RUN_BACKWARD -> RUN_FORWARD and RUN_FORWARD_BREAK shall not be possible, stop first
	elif status["STATE"] == State.RUN_BACKWARD:
		if new_state == State.RUN_FORWARD or new_state == State.RUN_FORWARD_BREAK:
			return False
	# STOP -> RUN_FORWARD_BREAK shall not be possible, has no sense
	elif status["STATE"] == State.STOP:
		if new_state == State.RUN_FORWARD_BREAK:
			return False
	# ERROR -> RUN_FORWARD_BREAK shall not be possible, has no sense
	elif status["STATE"] == State.ERROR:
		if new_state == State.RUN_FORWARD_BREAK:
			return False

	status["STATE"] = new_state
	return True
