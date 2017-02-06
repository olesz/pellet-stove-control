#!/usr/bin/env python

###########
# imports
###########
import RPi.GPIO as GPIO
import time
import ConfigParser
import os
import signal
import sys
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
	
class Gpio_outputs(Enum):
	LOAD = "load-motor"
	LOAD_REVERSE = "load-motor-reverse"
	VENTILLATOR = "ventillator"
	PUMP = "pump"
	
class Gpio_inputs(Enum):
	ROTATION = "rotation-check"
	THERMOSTAT = "termostat-check"
	OVERHEAT = "overheat-check"
	PHASE1 = "phase-check-phase1"
	PHASE2 = "phase-check-phase2"
	PHASE3 = "phase-check-phase3"

###########
# init part
###########
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
STATUS = {
	"STATE": State.RUN_FORWARD,
	"STATUS_MESSAGE": ""
	}

GPIO.setmode(GPIO.BOARD)

###########
# functions
###########

###########
# GPIO input callbacks
def gpio_input_callback_error(channel):
	global STATUS
	global CONFIG

	set_new_state(State.ERROR)

	for input_gpio_name in Gpio_inputs:
		if CONFIG.getint(input_gpio_name.value,"gpio") == channel:
			STATUS["STATUS_MESSAGE"] = input_gpio_name.value

def gpio_input_callback_stop(channel):
	global STATUS
	global CONFIG

	for input_gpio_name in Gpio_inputs:
		if CONFIG.getint(input_gpio_name.value,"gpio") == channel:
			if check_if_inputs_enabled([input_gpio_name]) == [True]:
				set_new_state(State.STOP)
				STATUS["STATUS_MESSAGE"] = input_gpio_name.value
			else:
				set_new_state(State.RUN_FORWARD)
				STATUS["STATUS_MESSAGE"] = ""

def read_config(signum = None, frame = None):
	global CONFIG
	
	CONFIG = ConfigParser.ConfigParser()
	CONFIG.read(os.path.join(SCRIPT_DIR,"..","config","config.ini"))

def write_config():
	pass

def disable_outputs(goutputs = [e for e in Gpio_outputs]):
	global CONFIG
	
	# setting output GPIOs to low before exit
	for goutput in goutputs:
		GPIO.output(CONFIG.getint(goutput.value,"gpio"), GPIO.HIGH)

def enable_outputs(goutputs = [e for e in Gpio_outputs]):
	global CONFIG
	
	# setting output GPIOs to low before exit
	for goutput in goutputs:
		GPIO.output(CONFIG.getint(goutput.value,"gpio"), GPIO.LOW)

def check_if_inputs_enabled(ginputs = [e for e in Gpio_inputs]):
	global CONFIG
	result = []
	
	for ginput in ginputs:
		if CONFIG.get(ginput.value,"mode") == "no":
			result.append(GPIO.input(CONFIG.getint(ginput.value,"gpio")) == GPIO.HIGH)
		else:
			result.append(GPIO.input(CONFIG.getint(ginput.value,"gpio")) == GPIO.LOW)
			
	return result

def check_if_outputs_enabled(goutputs = [e for e in Gpio_outputs]):
	global CONFIG
	result = []
	
	for goutput in goutputs:
		result.append(GPIO.input(CONFIG.getint(goutput.value,"gpio")) == GPIO.LOW)	
	return result

def cleanup(signum = None, frame = None):
	disable_outputs()
	GPIO.cleanup()
	# exit is needed because otherwise some GPIO commands could be executed before
	# program termination causing runtime exception
	sys.exit()
	
def initialize_input_gpios(ginputs = [e for e in Gpio_inputs]):
	global CONFIG

	# setting input GPIOs based on enabled status
	for ginput in ginputs:
		if ginput in (Gpio_inputs.PHASE1, Gpio_inputs.PHASE2, Gpio_inputs.PHASE3, Gpio_inputs.THERMOSTAT):
			if CONFIG.getboolean(ginput.value,"enabled"):
				# "no" means normally open
				# config should be validated that it shall contain "no" and "nc" only
				if CONFIG.get(ginput.value,"mode") == "no":
					GPIO.setup(CONFIG.getint(ginput.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
					GPIO.add_event_detect(CONFIG.getint(ginput.value,"gpio"), GPIO.BOTH, callback=gpio_input_callback_stop, bouncetime=100)
				else:
					GPIO.setup(CONFIG.getint(ginput.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
					GPIO.add_event_detect(CONFIG.getint(ginput.value,"gpio"), GPIO.BOTH, callback=gpio_input_callback_stop, bouncetime=100)
				
		if ginput in (Gpio_inputs.ROTATION, Gpio_inputs.OVERHEAT):
			if CONFIG.getboolean(ginput.value,"enabled"):
				# "no" means normally open
				# config should be validated that it shall contain "no" and "nc" only
				if CONFIG.get(ginput.value,"mode") == "no":
					GPIO.setup(CONFIG.getint(ginput.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
					GPIO.add_event_detect(CONFIG.getint(ginput.value,"gpio"), GPIO.RISING, callback=gpio_input_callback_error, bouncetime=100)
				else:
					GPIO.setup(CONFIG.getint(ginput.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
					GPIO.add_event_detect(CONFIG.getint(ginput.value,"gpio"), GPIO.FALLING, callback=gpio_input_callback_error, bouncetime=100)

def initialize_output_gpios(goutputs = [e for e in Gpio_outputs]):
	global CONFIG

	# setting output GPIOs
	for goutput in goutputs:
		GPIO.setup(CONFIG.getint(goutput.value,"gpio"), GPIO.OUT, initial = GPIO.HIGH)

def set_new_state(new_state):
	global STATUS
	
	# RUN_FORWARD -> RUN_BACKWARD shall not be possible, stop first
	if STATUS["STATE"] == State.RUN_FORWARD:
		if new_state == State.RUN_BACKWARD:
			return False
	# RUN_FORWARD_BREAK -> RUN_BACKWARD shall not be possible, stop first
	elif STATUS["STATE"] == State.RUN_FORWARD_BREAK:
		if new_state == State.RUN_BACKWARD:
			return False
	# RUN_BACKWARD -> RUN_FORWARD and RUN_FORWARD_BREAK shall not be possible, stop first
	elif STATUS["STATE"] == State.RUN_BACKWARD:
		if new_state == State.RUN_FORWARD or net_state == State.RUN_FORWARD_BREAK:
			return False
	# STOP -> RUN_FORWARD_BREAK shall not be possible, has no sense
	elif STATUS["STATE"] == State.STOP:
		if new_state == State.RUN_FORWARD_BREAK:
			return False
	# ERROR -> RUN_FORWARD_BREAK shall not be possible, has no sense
	elif STATUS["STATE"] == State.ERROR:
		if new_state == State.RUN_FORWARD_BREAK:
			return False

	STATUS["STATE"] = new_state
	return True

###########
# main part
###########
# add signal handlers
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)
# read config from and start over if SIGUSR1 is received
signal.signal(signal.SIGUSR1, read_config)

# read config
read_config()

# set timers to values from config
TIMER = 1

initialize_input_gpios()
initialize_output_gpios()

print check_if_inputs_enabled()
print check_if_outputs_enabled()
	

# main loop
while True:
	print STATUS["STATE"], TIMER
	
	if STATUS["STATE"] == State.RUN_FORWARD:
		if TIMER < CONFIG.getint("timing","load_time"):
			enable_outputs([Gpio_outputs.LOAD])
			enable_outputs([Gpio_outputs.VENTILLATOR])
			enable_outputs([Gpio_outputs.PUMP])
			TIMER += 1
		else:
			TIMER = 1
			set_new_state(State.RUN_FORWARD_BREAK)
	elif STATUS["STATE"] == State.RUN_FORWARD_BREAK:
		if TIMER < CONFIG.getint("timing","load_time"):
			disable_outputs([Gpio_outputs.LOAD])
			enable_outputs([Gpio_outputs.VENTILLATOR])
			enable_outputs([Gpio_outputs.PUMP])
			TIMER += 1
		else:
			TIMER = 1
			set_new_state(State.RUN_FORWARD)
	elif STATUS["STATE"] == State.RUN_BACKWARD:
		disable_outputs()
		enable_outputs([Gpio_outputs.LOAD_REVERSE])
	elif STATUS["STATE"] == State.STOP:
		disable_outputs()
		TIMER = 1
	elif STATUS["STATE"] == State.ERROR:
		disable_outputs()
		TIMER = 1
	
	time.sleep(1)

# calling cleanup
cleanup()
