#!/usr/bin/env python

###########
# imports
###########
from enum import Enum
from threading import Thread
import re
import select
import socket
import time

import tcpclient

###########
# internal classes
###########
class ConnCheck(Enum):
	READ = 1
	WRITE = 2

class ClientThread(Thread):

	conn = None
	conn_ok = True
	response = None
	response_text = None

	timeout = 0.1
	# tune these if longer commands are needed
	# do not tune recv_lenght because it can miss \r\n (or the beginning of the next command)
	recv_lenght = 1
	chunk_size = 40

	def __init__(self, conn):
		Thread.__init__(self)
		self.conn = conn

	def run(self):
		pattern_status_notif = re.compile('NOTIFY-STATUS [A-Z_]+ [0-9]+ [0-9]+ [A-Za-z0-9_]*')
		pattern_status_response = re.compile('STATUS [A-Z_]+ [0-9]+ [0-9]+ [A-Za-z0-9_]*')

		try:
			while self.conn_ok:
				print self.conn_ok
				# check if socket is ready to read
				if self.check_connection(ConnCheck.READ):

					data = self.receive().rstrip('\n').rstrip('\r')
					print "received - " + data
					if data == 'OK':
						print "ok"
						self.response = True
					elif data == 'NOK':
						self.response = False
					elif pattern_status_response.match(data):
						self.response = True
					elif pattern_status_notif.match(data):
						tcpclient.status_changed_notification(data)

					self.response_text = data

		finally:
			if self.conn is not None:
				self.conn.shutdown(socket.SHUT_RDWR)
				self.close()

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

	def send_data(self, data, wait_for_response, response_is_boolean):
		#self.send("STATUS " + state.get_state().name + " " + 
		#	config.get("timing","load_time") + " " + config.get("timing","load_break_time") +
		#	" " + state.get_status_message() + "\r\n")
		self.response = None
		self.response_text = None

		self.send(data)

		if wait_for_response:
			# we wait 10 sec for a reply
			for x in xrange(1, 100):
				if not self.conn_ok:
					break
				if self.response is not None:
					if response_is_boolean:
						return self.response
					else:
						print "xx"
						return self.response_text

				time.sleep(0.1)

			# timeout waiting for a response
			if response_is_boolean:
				return False
			else:
				print "none1"
				return None
		else:
			print "none2"
			return None

	def send(self, msg):
		totalsent = 0
	
		while totalsent < len(msg) and self.conn_ok:
			print "yyyyyyy"
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
			print "xxxxxxx" + ''.join(chunks)
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

	def close(self):
		self.conn_ok = False
