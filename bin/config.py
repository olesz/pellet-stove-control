#!/usr/bin/env python

###########
# imports
###########
import ConfigParser
import os
import threading

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

def get(a,b):
	return CONFIG.get(a,b)

def getint(a,b):
	return CONFIG.getint(a,b)

def getboolean(a,b):
	return CONFIG.getboolean(a,b)

def set(a,b,c):
	global LOCK
	
	LOCK.acquire()
	
	try:
		CONFIG.set(a,b,c)
	finally:
		LOCK.release()
