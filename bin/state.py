#!/usr/bin/env python

###########
# imports
###########
from enum import Enum
import threading

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
# init part
###########
STATE = {
	"STATE": State.RUN_FORWARD,
	"STATUS_MESSAGE": ""
	}
LOCK = threading.RLock()

###########
# functions
###########
def set_new_state(new_state):
	global LOCK
	result = True

	LOCK.acquire()
	
	try:
		# RUN_FORWARD -> RUN_BACKWARD shall not be possible, stop first
		if STATE["STATE"] == State.RUN_FORWARD:
			if new_state == State.RUN_BACKWARD:
				result = False
		# RUN_FORWARD_BREAK -> RUN_BACKWARD shall not be possible, stop first
		elif STATE["STATE"] == State.RUN_FORWARD_BREAK:
			if new_state == State.RUN_BACKWARD:
				result = False
		# RUN_BACKWARD -> RUN_FORWARD and RUN_FORWARD_BREAK shall not be possible, stop first
		elif STATE["STATE"] == State.RUN_BACKWARD:
			if new_state == State.RUN_FORWARD or new_state == State.RUN_FORWARD_BREAK:
				result = False
		# STOP -> RUN_FORWARD_BREAK shall not be possible, has no sense
		elif STATE["STATE"] == State.STOP:
			if new_state == State.RUN_FORWARD_BREAK:
				result = False
		# ERROR -> RUN_FORWARD_BREAK shall not be possible, has no sense
		elif STATE["STATE"] == State.ERROR:
			if new_state == State.RUN_FORWARD_BREAK:
				result = False
	finally:
		if result:
			STATE["STATE"] = new_state
		LOCK.release()
		return result

def get_state():
	return STATE["STATE"]

def set_status_message(message):
	STATE["STATUS_MESSAGE"] = message

def get_status_message():
	return STATE["STATUS_MESSAGE"]
