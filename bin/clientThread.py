#!/usr/bin/env python

###########
# imports
###########
from threading import Thread
import re
import select

import state
import config

class ClientThread(Thread):

	conn = None
	conn_ok = True
	subscribed = False
	notify = False

	def __init__(self, conn):
		Thread.__init__(self)
		self.conn = conn

	def run(self):
		pattern_set_load_time = re.compile('LOAD_TIME [0-9]+')
		pattern_set_load_break_time = re.compile('LOAD_BREAK_TIME [0-9]+')

		try:
			while self.conn_ok:
				# check if socket is ready to read
			    	ready = select.select([self.conn], [], [], 1)
				if ready[0]:
					command_success = True
				
					data = self.receive().rstrip('\n').rstrip('\r')

	                		if data == 'STOP':
						command_success = state.set_new_state(state.State.STOP)
					elif data == 'START':
						command_success = state.set_new_state(state.State.RUN_FORWARD)
					elif data == 'REVERSE':
						command_success = state.set_new_state(state.State.RUN_BACKWARD)
					elif data == 'STATUS':
						self.send_status()
					elif data == 'SUBSCRIBE':
						self.subscribed = True
						# set notify to False not to send a status report direct after subscribe	
						self.notify = False
					elif data == 'UNSUBSCRIBE':
						self.subscribed = False
					elif pattern_set_load_time.match(data):
						config.set("timing","load_time", data.split()[1])
						config.write_config()
					elif pattern_set_load_break_time.match(data):
						config.set("timing","load_break_time", data.split()[1])
						config.write_config()
					else:
						command_success = False

					if command_success:
						self.send("OK\r\n")
					else:
						self.send("NOK\r\n")
				
				# check if ready to write
				if self.notify and self.subscribed:
					self.send_status()
					self.notify = False
					
		finally:
			if self.conn is not None:
				self.conn.shutdown(SHUT_RDWR)
				self.conn.close()

	def send_status(self):
		self.send("STATUS " + state.STATE["STATE"].name + " " + 
			config.get("timing","load_time") + " " + config.get("timing","load_break_time") + "\r\n")

	def send(self, msg):
		totalsent = 0
	
		while totalsent < len(msg):
			try:
				sent = self.conn.send(msg[totalsent:])
			except socket.error:
				self.conn_ok = False
			if sent == 0:
				self.conn_ok = False
			totalsent = totalsent + sent

	def receive(self):
		chunks = []
	
		pattern_line_end = re.compile('.*\r\n')
	
		while not pattern_line_end.match(''.join(chunks)):
			try:
				chunk = self.conn.recv(128)
			except socket.error:
				self.conn_ok = False
			if chunk == '':
				self.conn_ok = False
			chunks.append(chunk)
		return ''.join(chunks)

	def notifyStatus(self):
		self.notify = True
