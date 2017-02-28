#!/usr/bin/env python

###########
# imports
###########
from enum import Enum
from threading import Thread
import re
import select
import socket

import state
import config
import tcpserver

###########
# internal classes
###########
class ConnCheck(Enum):
	READ = 1
	WRITE = 2

class CommandSuccess(Enum):
	OK = 1
	NOK = 2
	DO_NOT_SEND = 3

class ClientThread(Thread):

	conn = None
	conn_ok = True
	subscribed = False
	notify = False

	timeout = 0.1
	# tune these if longer commands are needed
	# do not tune recv_lenght because it can miss \r\n (or the beginning of the next command)
	recv_lenght = 1
	chunk_size = 40

	def __init__(self, conn):
		Thread.__init__(self)
		self.conn = conn

	def run(self):
		pattern_set_load_time = re.compile('LOAD_TIME [0-9]+')
		pattern_set_load_break_time = re.compile('LOAD_BREAK_TIME [0-9]+')
		pattern_data_id = re.compile('^([0-9A_Za-z]+-)(.*)$')

		try:
			while self.conn_ok:
				# check if socket is ready to read
				if self.check_connection(ConnCheck.READ):
					command_success = CommandSuccess.OK

					# initialize data_id, if there is no id in the command we concatenate the empty string
					data_id = ""
					data = self.receive().rstrip('\n').rstrip('\r')

					# get the id part if present
					data_id_match = pattern_data_id.match(data)
					# if there was a match then after the dash we have the command
					# and before it we have the command id
					if data_id_match:
						data_id = data_id_match.group(1)
						data = data_id_match.group(2)

					if data == 'STOP':
						command_success = CommandSuccess.OK if state.set_new_state(state.State.STOP) else CommandSuccess.NOK
					elif data == 'START':
						command_success = CommandSuccess.OK if state.set_new_state(state.State.RUN_FORWARD) else CommandSuccess.NOK
					elif data == 'REVERSE':
						command_success = CommandSuccess.OK if state.set_new_state(state.State.RUN_BACKWARD) else CommandSuccess.NOK
					elif data == 'STATUS':
						self.send_status(data_id)
						command_success = CommandSuccess.DO_NOT_SEND
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
						command_success = CommandSuccess.NOK

					if command_success is CommandSuccess.OK:
						if self.check_connection(ConnCheck.WRITE):
							self.send(str(data_id) + "OK\r\n")
					elif command_success is CommandSuccess.NOK:
						if self.check_connection(ConnCheck.WRITE):
							self.send(str(data_id) + "NOK\r\n")
					#elif command_success is CommandSuccess.DO_NOT_SEND:
					#	pass

				# check if ready to write
				if self.notify and self.subscribed:
					if self.check_connection(ConnCheck.WRITE):
						self.send_status("NOTIFY-")
					self.notify = False
					
		finally:
			if self.conn is not None:
				self.conn.shutdown(socket.SHUT_RDWR)
				self.conn.close()
			tcpserver.threadlist_remove(self)

	def check_connection(self, action):

		if action == ConnCheck.READ:
			ready = select.select([self.conn], [], [], self.timeout)
			if ready[0]:
				return True
		elif action == ConnCheck.WRITE:
			ready = select.select([], [self.conn], [], self.timeout)
			if ready[1]:
				return True
		return False

	def send_status(self, data_id = ""):
		self.send(str(data_id) + "STATUS " + state.get_state().name + " " + 
			config.get("timing","load_time") + " " + config.get("timing","load_break_time") +
			" " + state.get_status_message() + "\r\n")

	def send(self, msg):
		totalsent = 0
	
		while totalsent < len(msg) and self.conn_ok:
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
	
		while not pattern_line_end.match(''.join(chunks)) and self.conn_ok and len(chunks) < self.chunk_size:
			try:
				chunk = self.conn.recv(self.recv_lenght)
			except socket.error:
				self.conn_ok = False
			if chunk == '':
				self.conn_ok = False
			chunks.append(chunk)
		# return empty string if command was bigger than expected
		if len(chunks) < self.chunk_size:
			return ''.join(chunks)
		else:
			# drop the end of the long command
			while not pattern_line_end.match(''.join(chunks)) and self.conn_ok:
				try:
					 self.conn.recv(self.recv_lenght)
				except socket.error:
					self.conn_ok = False
			# return empty
			return ''

	def notify_status(self):
		self.notify = True
