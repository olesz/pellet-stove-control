#!/usr/bin/env python

###########
# imports
###########
import ConfigParser
import os

###########
# init part
###########
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def read_config(signum = None, frame = None):
	
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(SCRIPT_DIR,"..","config","config.ini"))
	
	return config

def write_config():
	pass
