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
	TERMOSTAT = "rotation-check"
	ROTATION = "termostat-check"
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
	"ERROR_MESSAGE": ""
	}

GPIO.setmode(GPIO.BOARD)

###########
# functions
###########
def read_config2():
	read_config()

def read_config():
	config_parser = ConfigParser.ConfigParser()
	config_parser.read(os.path.join(SCRIPT_DIR,"..","config","config.ini"))
	return config_parser

def write_config():
	pass

def disable_outputs():
	global CONFIG
	
	# setting output GPIOs to low before exit
	for output_gpio_name in Gpio_outputs:
		GPIO.output(CONFIG.getint(output_gpio_name.value,"gpio"), GPIO.HIGH)

def cleanup2(signum, frame):
	cleanup()

def cleanup():
	disable_outputs()
	GPIO.cleanup()
	# exit is needed because otherwise some GPIO commands could be executed before
	# program termination causing runtime exception
	sys.exit()

###########
# GPIO input callback
###########
def gpio_input_callback(channel):
	global STATUS
	global CONFIG

	STATUS["STATE"] = State.RUN_FORWARD

	for input_gpio_name in Gpio_inputs:
		if CONFIG.getint(input_gpio_name,"gpio") == channel:
			STATUS["ERROR_MESSAGE"] = "rotation-check"

###########
# main part
###########
# add signal handlers
signal.signal(signal.SIGTERM, cleanup2)
signal.signal(signal.SIGINT, cleanup2)
signal.signal(signal.SIGUSR1, read_config2)

# read config
CONFIG = read_config()

# set timers to values from config
TIMER = 0
STATUS["LOAD_TIMER"] = CONFIG.get("timing","load_time")
STATUS["LOAD_BREAK_TIMER"] = CONFIG.get("timing","load_break_time")

# setting input GPIOs based on enabled status
for input_gpio_name in Gpio_inputs:
	if CONFIG.getboolean(input_gpio_name.value,"enabled"):
		# "no" means normally open
		# config should be validated that it shall contain "no" and "nc" only
		if CONFIG.get(input_gpio_name.value,"mode") == "no":
			GPIO.setup(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
			GPIO.add_event_detect(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.RISING, callback=gpio_input_callback)
		else:
			GPIO.setup(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.add_event_detect(CONFIG.getint(input_gpio_name.value,"gpio"), GPIO.FALLING, callback=gpio_input_callback)
		

# setting output GPIOs
for output_gpio_name in Gpio_outputs:
	GPIO.setup(CONFIG.getint(output_gpio_name.value,"gpio"), GPIO.OUT, initial = GPIO.HIGH)

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
	elif STATUS["STATE"] == State.ERROR:
		disable_outputs()
	
	time.sleep(1)

# calling cleanup
cleanup()
