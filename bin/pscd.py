#!/usr/bin/env python

###########
# imports
###########
import RPi.GPIO as GPIO
import time
import signal
import sys
from enum import Enum
import threading

import state
import tcpserver
import config
	
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
GPIO.setmode(GPIO.BOARD)

###########
# functions
###########

###########
# GPIO input callbacks
def gpio_input_callback_error(channel):
	global CONFIG

	state.set_new_state(state.State.ERROR)

	for input_gpio_name in Gpio_inputs:
		if config.getint(input_gpio_name.value,"gpio") == channel:
			status.set_status_message(input_gpio_name.value)

def gpio_input_callback_stop(channel):
	global CONFIG

	for input_gpio_name in Gpio_inputs:
		if config.getint(input_gpio_name.value,"gpio") == channel:
			if check_if_inputs_enabled([input_gpio_name]) == [True]:
				state.set_new_state(state.State.STOP)
				status.set_status_message(input_gpio_name.value)
			else:
				state.set_new_state(state.State.RUN_FORWARD)
				status.set_status_message("")

def disable_outputs(goutputs = [e for e in Gpio_outputs]):
	global CONFIG
	
	# setting output GPIOs to low before exit
	for goutput in goutputs:
		GPIO.output(config.getint(goutput.value,"gpio"), GPIO.HIGH)

def enable_outputs(goutputs = [e for e in Gpio_outputs]):
	global CONFIG
	
	# setting output GPIOs to low before exit
	for goutput in goutputs:
		GPIO.output(config.getint(goutput.value,"gpio"), GPIO.LOW)

def check_if_inputs_enabled(ginputs = [e for e in Gpio_inputs]):
	global CONFIG
	result = []
	
	for ginput in ginputs:
		if config.get(ginput.value,"mode") == "no":
			result.append(GPIO.input(config.getint(ginput.value,"gpio")) == GPIO.HIGH)
		else:
			result.append(GPIO.input(config.getint(ginput.value,"gpio")) == GPIO.LOW)
			
	return result

def check_if_outputs_enabled(goutputs = [e for e in Gpio_outputs]):
	global CONFIG
	result = []
	
	for goutput in goutputs:
		result.append(GPIO.input(config.getint(goutput.value,"gpio")) == GPIO.LOW)	
	return result

def cleanup(signum = None, frame = None):
	disable_outputs()
	GPIO.cleanup()
	tcpserver.stop_socket()
	TCPTHREAD.join()
	# exit is needed because otherwise some GPIO commands could be executed before
	# program termination causing runtime exception
	sys.exit()
	
def initialize_input_gpios(ginputs = [e for e in Gpio_inputs]):
	global CONFIG

	# setting input GPIOs based on enabled status
	for ginput in ginputs:
		if ginput in (Gpio_inputs.PHASE1, Gpio_inputs.PHASE2, Gpio_inputs.PHASE3, Gpio_inputs.THERMOSTAT):
			if config.getboolean(ginput.value,"enabled"):
				# "no" means normally open
				# config should be validated that it shall contain "no" and "nc" only
				if config.get(ginput.value,"mode") == "no":
					GPIO.setup(config.getint(ginput.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
					GPIO.add_event_detect(config.getint(ginput.value,"gpio"), GPIO.BOTH, callback=gpio_input_callback_stop, bouncetime=100)
				else:
					GPIO.setup(config.getint(ginput.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
					GPIO.add_event_detect(config.getint(ginput.value,"gpio"), GPIO.BOTH, callback=gpio_input_callback_stop, bouncetime=100)
				
		if ginput in (Gpio_inputs.ROTATION, Gpio_inputs.OVERHEAT):
			if config.getboolean(ginput.value,"enabled"):
				# "no" means normally open
				# config should be validated that it shall contain "no" and "nc" only
				if config.get(ginput.value,"mode") == "no":
					GPIO.setup(config.getint(ginput.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
					GPIO.add_event_detect(config.getint(ginput.value,"gpio"), GPIO.RISING, callback=gpio_input_callback_error, bouncetime=100)
				else:
					GPIO.setup(config.getint(ginput.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
					GPIO.add_event_detect(config.getint(ginput.value,"gpio"), GPIO.FALLING, callback=gpio_input_callback_error, bouncetime=100)

def initialize_output_gpios(goutputs = [e for e in Gpio_outputs]):
	global CONFIG

	# setting output GPIOs
	for goutput in goutputs:
		GPIO.setup(config.getint(goutput.value,"gpio"), GPIO.OUT, initial = GPIO.HIGH)

###########
# main part
###########
# add signal handlers
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)
# read config from and start over if SIGUSR1 is received
signal.signal(signal.SIGUSR1, config.read_config)

# read config
CONFIG = config.read_config()

# set timers to values from config
TIMER = 1

initialize_input_gpios()
initialize_output_gpios()

#print check_if_inputs_enabled()
#print check_if_outputs_enabled()

TCPTHREAD = threading.Thread(target=tcpserver.start_socket)
TCPTHREAD.start()

# main loop
while True:
	print state.get_state(), TIMER
	
	if not TCPTHREAD.is_alive():
		break
	
	if state.get_state() == state.State.RUN_FORWARD:
		if TIMER <= config.getint("timing","load_time"):
			enable_outputs([Gpio_outputs.LOAD])
			enable_outputs([Gpio_outputs.VENTILLATOR])
			enable_outputs([Gpio_outputs.PUMP])
			TIMER += 1
		else:
			TIMER = 1
			state.set_new_state(state.State.RUN_FORWARD_BREAK)
	elif state.get_state() == state.State.RUN_FORWARD_BREAK:
		if TIMER <= config.getint("timing","load_break_time"):
			disable_outputs([Gpio_outputs.LOAD])
			enable_outputs([Gpio_outputs.VENTILLATOR])
			enable_outputs([Gpio_outputs.PUMP])
			TIMER += 1
		else:
			TIMER = 1
			state.set_new_state(state.State.RUN_FORWARD)
	elif state.get_state() == state.State.RUN_BACKWARD:
		disable_outputs()
		enable_outputs([Gpio_outputs.LOAD_REVERSE])
	elif state.get_state() == state.State.STOP:
		disable_outputs()
		TIMER = 1
	elif state.get_state() == state.State.ERROR:
		disable_outputs()
		TIMER = 1
	
	time.sleep(1)

# calling cleanup
cleanup()
