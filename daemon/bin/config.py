#!/usr/bin/env python

###########
# imports
###########
import ConfigParser
import os
import threading

import tcpserver

###########
# init part
###########
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG = None
LOCK = threading.RLock()

def read_config(signum = None, frame = None):
	global CONFIG
	global LOCK
	
	LOCK.acquire()
	
	try:
		CONFIG = ConfigParser.ConfigParser()
		CONFIG.read(os.path.join(SCRIPT_DIR,"..","config","config.ini"))
	finally:
		LOCK.release()

def write_config():
	global CONFIG
	
	cfgfile = open(os.path.join(SCRIPT_DIR,"..","config","config.ini"),'w')
	CONFIG.write(cfgfile)
	cfgfile.close()

def get(section, variable):
	return CONFIG.get(section, variable)

def getint(section, variable):
	return CONFIG.getint(section, variable)

def getboolean(section, variable):
	return CONFIG.getboolean(section, variable)

def set(section, variable, value):
	global LOCK
	
	LOCK.acquire()
	
	try:
		if section == "timing":
			tcpserver.set_notify(True)
		CONFIG.set(section,variable,value)
	finally:
		LOCK.release()
