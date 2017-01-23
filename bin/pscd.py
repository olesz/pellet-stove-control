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

	STATUS["STATE"] = State.ERROR

	for input_gpio_name in Gpio_inputs:
		if CONFIG.getint(input_gpio_name.value,"gpio") == channel:
			STATUS["STATUS_MESSAGE"] = input_gpio_name.value

def gpio_input_callback_stop(channel):
	global STATUS
	global CONFIG

	for input_gpio_name in Gpio_inputs:
		if CONFIG.getint(input_gpio_name.value,"gpio") == channel:
			# "no" means normally open
			# config should be validated that it shall contain "no" and "nc" only
			if CONFIG.get(input_gpio_name.value,"mode") == "no":
				if GPIO.input(channel):
					STATUS["STATE"] = State.STOP
					STATUS["STATUS_MESSAGE"] = input_gpio_name.value
				else:
					STATUS["STATE"] = State.RUN_FORWARD
					STATUS["STATUS_MESSAGE"] = ""
			else:
				if not GPIO.input(channel):
					STATUS["STATE"] = State.STOP
					STATUS["STATUS_MESSAGE"] = input_gpio_name.value
				else:
					STATUS["STATE"] = State.RUN_FORWARD
					STATUS["STATUS_MESSAGE"] = ""

def read_config():
	global CONFIG
	
	CONFIG = ConfigParser.ConfigParser()
	CONFIG.read(os.path.join(SCRIPT_DIR,"..","config","config.ini"))

def write_config():
	pass

def disable_outputs():
	global CONFIG
	
	# setting output GPIOs to low before exit
	for output_gpio_name in Gpio_outputs:
		GPIO.output(CONFIG.getint(output_gpio_name.value,"gpio"), GPIO.HIGH)

def cleanup():
	disable_outputs()
	GPIO.cleanup()
	# exit is needed because otherwise some GPIO commands could be executed before
	# program termination causing runtime exception
	sys.exit()
	
def initialize_input_gpios():
	global CONFIG

	# setting input GPIOs based on enabled status
	for input_gpio_name in (Gpio_inputs.PHASE1, Gpio_inputs.PHASE2, Gpio_inputs.PHASE3, Gpio_inputs.THERMOSTAT):
		if CONFIG.getboolean(input_gpio_name.value,"enabled"):
			# "no" means normally open
			# config should be validated that it shall contain "no" and "nc" only
			if CONFIG.get(input_gpio_name.value,"mode") == "no":
				GPIO.setup(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
				GPIO.add_event_detect(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.BOTH, callback=gpio_input_callback_stop, bouncetime=100)
			else:
				GPIO.setup(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_UP)
				GPIO.add_event_detect(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.BOTH, callback=gpio_input_callback_stop, bouncetime=100)
				
	for input_gpio_name in (Gpio_inputs.ROTATION, Gpio_inputs.OVERHEAT):
		if CONFIG.getboolean(input_gpio_name.value,"enabled"):
			# "no" means normally open
			# config should be validated that it shall contain "no" and "nc" only
			if CONFIG.get(input_gpio_name.value,"mode") == "no":
				GPIO.setup(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
				GPIO.add_event_detect(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.RISING, callback=gpio_input_callback_error, bouncetime=100)
			else:
				GPIO.setup(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
				GPIO.add_event_detect(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.FALLING, callback=gpio_input_callback_error, bouncetime=100)

def initialize_output_gpios():
	global CONFIG

	# setting output GPIOs
	for output_gpio_name in Gpio_outputs:
		GPIO.setup(CONFIG.getint(output_gpio_name.value,"gpio"), GPIO.OUT, initial = GPIO.HIGH)

###########
# signal helpers
def cleanup2(signum, frame):
	cleanup()

def read_config2(signum, frame):
	read_config()

###########
# main part
###########
# add signal handlers
signal.signal(signal.SIGTERM, cleanup2)
signal.signal(signal.SIGINT, cleanup2)
# read config from and start over if SIGUSR1 is received
signal.signal(signal.SIGUSR1, read_config2)

# read config
read_config()

# set timers to values from config
TIMER = 0

initialize_input_gpios()
initialize_output_gpios()

# main loop
while True:
	print STATUS["STATE"], TIMER
	if STATUS["STATE"] == State.RUN_FORWARD:
		if TIMER < CONFIG.getint("timing","load_time"):
			GPIO.output(CONFIG.getint(Gpio_outputs.LOAD.value,"gpio"), GPIO.LOW)
			GPIO.output(CONFIG.getint(Gpio_outputs.VENTILLATOR.value,"gpio"), GPIO.LOW)
			GPIO.output(CONFIG.getint(Gpio_outputs.PUMP.value,"gpio"), GPIO.LOW)
			TIMER += 1
		else:
			TIMER = 0
			STATUS["STATE"] = State.RUN_FORWARD_BREAK
	elif STATUS["STATE"] == State.RUN_FORWARD_BREAK:
		if TIMER < CONFIG.getint("timing","load_time"):
			GPIO.output(CONFIG.getint(Gpio_outputs.LOAD.value,"gpio"), GPIO.HIGH)
			GPIO.output(CONFIG.getint(Gpio_outputs.VENTILLATOR.value,"gpio"), GPIO.LOW)
			GPIO.output(CONFIG.getint(Gpio_outputs.PUMP.value,"gpio"), GPIO.LOW)
			TIMER += 1
		else:
			TIMER = 0
			STATUS["STATE"] = State.RUN_FORWARD
	elif STATUS["STATE"] == State.RUN_BACKWARD:
		disable_outputs()
		GPIO.output(CONFIG.getint(Gpio_outputs.LOAD_REVERSE.value,"gpio"), GPIO.HIGH)
	elif STATUS["STATE"] == State.STOP:
		disable_outputs()
		TIMER = 0
	elif STATUS["STATE"] == State.ERROR:
		disable_outputs()
		TIMER = 0
	
	time.sleep(1)

# calling cleanup
cleanup()
